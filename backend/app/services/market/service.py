import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.config import settings
from app.models.market import CryptoAsset, MarketSnapshot, OHLCVCandle
from app.schemas.market import (
    TimeframeEnum,
    AssetResponse,
    PriceResponse,
    MarketSnapshotResponse,
    CandleResponse,
    OHLCVResponse,
    FreshnessMetadata,
)
from app.services.market.manager import provider_manager
from app.services.market.cache import market_cache
from app.services.market.validator import validator
from app.services.market.freshness import freshness_policy
from app.services.market.base import AssetNotFoundException

logger = logging.getLogger("market.service")

class MarketDataService:
    """
    High-level business service orchestrating asset registry, caching,
    data validation, persistence, and external market providers.
    """

    @staticmethod
    def get_or_create_asset(
        db: Session,
        symbol: str,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        provider_id: Optional[str] = None,
    ) -> CryptoAsset:
        clean_sym = symbol.upper().strip()
        asset = db.query(CryptoAsset).filter(
            (CryptoAsset.symbol == clean_sym) | (CryptoAsset.slug == (slug or clean_sym.lower()))
        ).first()

        if not asset:
            asset = CryptoAsset(
                symbol=clean_sym,
                name=name or f"{clean_sym} Crypto Asset",
                slug=slug or clean_sym.lower(),
                provider_id=provider_id or clean_sym.lower(),
                status="active",
                is_active=True,
            )
            db.add(asset)
            db.commit()
            db.refresh(asset)
            logger.info("Registered new crypto asset in database: %s (%s)", asset.symbol, asset.id)

        return asset

    @staticmethod
    def resolve_asset(db: Session, identifier: str) -> CryptoAsset:
        clean_id = identifier.strip()
        asset = db.query(CryptoAsset).filter(
            (CryptoAsset.id == clean_id)
            | (CryptoAsset.symbol == clean_id.upper())
            | (CryptoAsset.slug == clean_id.lower())
        ).first()

        if not asset:
            # Fallback auto-registration for standard symbols
            asset = MarketDataService.get_or_create_asset(db, symbol=clean_id)
        return asset

    @staticmethod
    def list_assets(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = "active",
        search: Optional[str] = None,
    ) -> Tuple[List[AssetResponse], int]:
        query = db.query(CryptoAsset)

        if status:
            query = query.filter(CryptoAsset.status == status)

        if search:
            search_term = f"%{search.strip().lower()}%"
            query = query.filter(
                (func.lower(CryptoAsset.symbol).like(search_term))
                | (func.lower(CryptoAsset.name).like(search_term))
            )

        total = query.count()
        assets = query.order_by(CryptoAsset.rank.asc().nullslast(), CryptoAsset.symbol.asc()).offset(skip).limit(limit).all()

        responses = []
        for a in assets:
            meta = json.loads(a.metadata_json) if a.metadata_json else None
            responses.append(
                AssetResponse(
                    id=a.id,
                    symbol=a.symbol,
                    name=a.name,
                    slug=a.slug,
                    provider_id=a.provider_id,
                    asset_type=a.asset_type,
                    status=a.status,
                    is_active=a.is_active,
                    rank=a.rank,
                    metadata=meta,
                    created_at=a.created_at,
                    updated_at=a.updated_at,
                )
            )
        return responses, total

    @staticmethod
    async def get_current_price(db: Session, identifier: str) -> PriceResponse:
        asset = MarketDataService.resolve_asset(db, identifier)
        cache_key = market_cache.price_key(asset.symbol)

        # 1. Check cache
        cached_data, cached_at = market_cache.get_with_cached_at(cache_key)
        if cached_data:
            freshness = freshness_policy.evaluate_freshness(
                source_timestamp=cached_data["source_timestamp"],
                ingested_at=cached_data["ingested_at"],
                provider=cached_data["provider"],
                data_type="price",
                cached_at=cached_at,
            )
            return PriceResponse(
                symbol=asset.symbol,
                asset_id=asset.id,
                price=cached_data["price"],
                price_change_24h=cached_data.get("price_change_24h"),
                price_change_percentage_24h=cached_data.get("price_change_percentage_24h"),
                high_24h=cached_data.get("high_24h"),
                low_24h=cached_data.get("low_24h"),
                volume_24h=cached_data.get("volume_24h"),
                freshness=freshness,
            )

        # 2. Fetch from Provider
        normalized = await provider_manager.get_current_price(asset.symbol)
        is_valid, error = validator.validate_price(normalized)
        if not is_valid:
            logger.warning("Price validation failed for '%s': %s", asset.symbol, error)

        ingested_at = datetime.now(timezone.utc)
        freshness = freshness_policy.evaluate_freshness(
            source_timestamp=normalized.source_timestamp,
            ingested_at=ingested_at,
            provider=normalized.provider,
            data_type="price",
        )

        price_dict = {
            "price": normalized.price,
            "price_change_24h": normalized.price_change_24h,
            "price_change_percentage_24h": normalized.price_change_percentage_24h,
            "high_24h": normalized.high_24h,
            "low_24h": normalized.low_24h,
            "volume_24h": normalized.volume_24h,
            "source_timestamp": normalized.source_timestamp,
            "ingested_at": ingested_at,
            "provider": normalized.provider,
        }

        # 3. Store in Cache
        ttl = getattr(settings, "MARKET_CACHE_PRICE_TTL_SECONDS", 15)
        market_cache.set(cache_key, price_dict, ttl_seconds=ttl)

        return PriceResponse(
            symbol=asset.symbol,
            asset_id=asset.id,
            price=normalized.price,
            price_change_24h=normalized.price_change_24h,
            price_change_percentage_24h=normalized.price_change_percentage_24h,
            high_24h=normalized.high_24h,
            low_24h=normalized.low_24h,
            volume_24h=normalized.volume_24h,
            freshness=freshness,
        )

    @staticmethod
    async def get_market_snapshot(db: Session, identifier: str) -> MarketSnapshotResponse:
        asset = MarketDataService.resolve_asset(db, identifier)
        cache_key = market_cache.snapshot_key(asset.symbol)

        # 1. Check cache
        cached_data, cached_at = market_cache.get_with_cached_at(cache_key)
        if cached_data:
            freshness = freshness_policy.evaluate_freshness(
                source_timestamp=cached_data["data_timestamp"],
                ingested_at=cached_data["ingested_at"],
                provider=cached_data["provider"],
                data_type="snapshot",
                cached_at=cached_at,
            )
            return MarketSnapshotResponse(
                id=cached_data.get("id"),
                asset_id=asset.id,
                symbol=asset.symbol,
                name=asset.name,
                price=cached_data["price"],
                market_cap=cached_data.get("market_cap"),
                volume_24h=cached_data.get("volume_24h"),
                price_change_24h=cached_data.get("price_change_24h"),
                price_change_percentage_24h=cached_data.get("price_change_percentage_24h"),
                high_24h=cached_data.get("high_24h"),
                low_24h=cached_data.get("low_24h"),
                circulating_supply=cached_data.get("circulating_supply"),
                total_supply=cached_data.get("total_supply"),
                data_timestamp=cached_data["data_timestamp"],
                freshness=freshness,
            )

        # 2. Fetch from Provider
        normalized = await provider_manager.get_market_snapshot(asset.symbol)
        is_valid, error = validator.validate_snapshot(normalized)
        if not is_valid:
            logger.warning("Snapshot validation warning for '%s': %s", asset.symbol, error)

        ingested_at = datetime.now(timezone.utc)

        # 3. Persist to DB
        snapshot_db = MarketSnapshot(
            asset_id=asset.id,
            price=normalized.price,
            market_cap=normalized.market_cap,
            volume_24h=normalized.volume_24h,
            price_change_24h=normalized.price_change_24h,
            price_change_percentage_24h=normalized.price_change_percentage_24h,
            high_24h=normalized.high_24h,
            low_24h=normalized.low_24h,
            circulating_supply=normalized.circulating_supply,
            total_supply=normalized.total_supply,
            provider=normalized.provider,
            data_timestamp=normalized.source_timestamp,
            ingested_at=ingested_at,
        )
        try:
            db.add(snapshot_db)
            db.commit()
            db.refresh(snapshot_db)
            snapshot_id = snapshot_db.id
        except Exception as e:
            db.rollback()
            logger.error("Failed to persist market snapshot to database: %s", str(e))
            snapshot_id = None

        freshness = freshness_policy.evaluate_freshness(
            source_timestamp=normalized.source_timestamp,
            ingested_at=ingested_at,
            provider=normalized.provider,
            data_type="snapshot",
        )

        snapshot_dict = {
            "id": snapshot_id,
            "price": normalized.price,
            "market_cap": normalized.market_cap,
            "volume_24h": normalized.volume_24h,
            "price_change_24h": normalized.price_change_24h,
            "price_change_percentage_24h": normalized.price_change_percentage_24h,
            "high_24h": normalized.high_24h,
            "low_24h": normalized.low_24h,
            "circulating_supply": normalized.circulating_supply,
            "total_supply": normalized.total_supply,
            "data_timestamp": normalized.source_timestamp,
            "ingested_at": ingested_at,
            "provider": normalized.provider,
        }

        # 4. Cache
        ttl = getattr(settings, "MARKET_CACHE_SNAPSHOT_TTL_SECONDS", 60)
        market_cache.set(cache_key, snapshot_dict, ttl_seconds=ttl)

        return MarketSnapshotResponse(
            id=snapshot_id,
            asset_id=asset.id,
            symbol=asset.symbol,
            name=asset.name,
            price=normalized.price,
            market_cap=normalized.market_cap,
            volume_24h=normalized.volume_24h,
            price_change_24h=normalized.price_change_24h,
            price_change_percentage_24h=normalized.price_change_percentage_24h,
            high_24h=normalized.high_24h,
            low_24h=normalized.low_24h,
            circulating_supply=normalized.circulating_supply,
            total_supply=normalized.total_supply,
            data_timestamp=normalized.source_timestamp,
            freshness=freshness,
        )

    @staticmethod
    async def get_ohlcv(
        db: Session,
        identifier: str,
        timeframe: TimeframeEnum,
        limit: int = 100,
    ) -> OHLCVResponse:
        asset = MarketDataService.resolve_asset(db, identifier)
        cache_key = market_cache.ohlcv_key(asset.symbol, timeframe.value, limit)

        # 1. Check cache
        cached_data, cached_at = market_cache.get_with_cached_at(cache_key)
        if cached_data:
            freshness = freshness_policy.evaluate_freshness(
                source_timestamp=cached_data["latest_timestamp"],
                ingested_at=cached_data["ingested_at"],
                provider=cached_data["provider"],
                data_type="ohlcv",
                timeframe=timeframe,
                cached_at=cached_at,
            )
            return OHLCVResponse(
                symbol=asset.symbol,
                asset_id=asset.id,
                timeframe=timeframe,
                count=len(cached_data["candles"]),
                candles=[CandleResponse(**c) for c in cached_data["candles"]],
                freshness=freshness,
            )

        # 2. Fetch from Provider
        raw_candles = await provider_manager.get_ohlcv(asset.symbol, timeframe, limit=limit)
        clean_candles = validator.sanitize_candles(raw_candles)

        ingested_at = datetime.now(timezone.utc)
        latest_ts = clean_candles[-1].timestamp if clean_candles else ingested_at
        provider_name = clean_candles[0].provider if clean_candles else "unknown"

        # 3. Persist latest candles to DB with duplicate skipping
        for c in clean_candles[-50:]:  # Persist recent candles to keep historical baseline
            existing = db.query(OHLCVCandle).filter(
                OHLCVCandle.asset_id == asset.id,
                OHLCVCandle.timeframe == timeframe.value,
                OHLCVCandle.candle_timestamp == c.timestamp,
                OHLCVCandle.provider == c.provider,
            ).first()
            if not existing:
                candle_db = OHLCVCandle(
                    asset_id=asset.id,
                    timeframe=timeframe.value,
                    open=c.open,
                    high=c.high,
                    low=c.low,
                    close=c.close,
                    volume=c.volume,
                    candle_timestamp=c.timestamp,
                    provider=c.provider,
                    ingested_at=ingested_at,
                )
                db.add(candle_db)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.debug("Database candle persistence handled: %s", str(e))

        candle_responses = [
            CandleResponse(
                timestamp=c.timestamp,
                open=c.open,
                high=c.high,
                low=c.low,
                close=c.close,
                volume=c.volume,
            )
            for c in clean_candles
        ]

        freshness = freshness_policy.evaluate_freshness(
            source_timestamp=latest_ts,
            ingested_at=ingested_at,
            provider=provider_name,
            data_type="ohlcv",
            timeframe=timeframe,
        )

        # 4. Cache
        ttl = getattr(settings, "MARKET_CACHE_OHLCV_TTL_SECONDS", 60)
        market_cache.set(
            cache_key,
            {
                "candles": [c.model_dump() for c in candle_responses],
                "latest_timestamp": latest_ts,
                "ingested_at": ingested_at,
                "provider": provider_name,
            },
            ttl_seconds=ttl,
        )

        return OHLCVResponse(
            symbol=asset.symbol,
            asset_id=asset.id,
            timeframe=timeframe,
            count=len(candle_responses),
            candles=candle_responses,
            freshness=freshness,
        )

    @staticmethod
    async def get_historical_ohlcv(
        db: Session,
        identifier: str,
        timeframe: TimeframeEnum,
        start_time: datetime,
        end_time: datetime,
        limit: int = 500,
    ) -> OHLCVResponse:
        asset = MarketDataService.resolve_asset(db, identifier)

        # 1. Query database first
        db_candles = db.query(OHLCVCandle).filter(
            OHLCVCandle.asset_id == asset.id,
            OHLCVCandle.timeframe == timeframe.value,
            OHLCVCandle.candle_timestamp >= start_time,
            OHLCVCandle.candle_timestamp <= end_time,
        ).order_by(OHLCVCandle.candle_timestamp.asc()).limit(limit).all()

        if len(db_candles) >= min(limit, 50):
            candle_res = [
                CandleResponse(
                    timestamp=c.candle_timestamp,
                    open=c.open,
                    high=c.high,
                    low=c.low,
                    close=c.close,
                    volume=c.volume,
                )
                for c in db_candles
            ]
            latest_ts = db_candles[-1].candle_timestamp
            freshness = freshness_policy.evaluate_freshness(
                source_timestamp=latest_ts,
                ingested_at=db_candles[-1].ingested_at,
                provider="database",
                data_type="ohlcv",
                timeframe=timeframe,
            )
            return OHLCVResponse(
                symbol=asset.symbol,
                asset_id=asset.id,
                timeframe=timeframe,
                count=len(candle_res),
                candles=candle_res,
                freshness=freshness,
            )

        # 2. Fetch from provider if not in database
        raw_candles = await provider_manager.get_historical_data(asset.symbol, timeframe, start_time, end_time)
        clean_candles = validator.sanitize_candles(raw_candles)[:limit]
        ingested_at = datetime.now(timezone.utc)
        latest_ts = clean_candles[-1].timestamp if clean_candles else ingested_at
        provider_name = clean_candles[0].provider if clean_candles else "unknown"

        candle_responses = [
            CandleResponse(
                timestamp=c.timestamp,
                open=c.open,
                high=c.high,
                low=c.low,
                close=c.close,
                volume=c.volume,
            )
            for c in clean_candles
        ]

        freshness = freshness_policy.evaluate_freshness(
            source_timestamp=latest_ts,
            ingested_at=ingested_at,
            provider=provider_name,
            data_type="ohlcv",
            timeframe=timeframe,
        )

        return OHLCVResponse(
            symbol=asset.symbol,
            asset_id=asset.id,
            timeframe=timeframe,
            count=len(candle_responses),
            candles=candle_responses,
            freshness=freshness,
        )

market_service = MarketDataService()

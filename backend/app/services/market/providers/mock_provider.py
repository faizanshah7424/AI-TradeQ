import math
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from app.schemas.market import TimeframeEnum
from app.services.market.base import (
    BaseMarketDataProvider,
    AssetNotFoundException,
)
from app.services.market.models import (
    NormalizedAsset,
    NormalizedPrice,
    NormalizedSnapshot,
    NormalizedCandle,
)

class MockMarketDataProvider(BaseMarketDataProvider):
    """
    Deterministic, high-fidelity mock market data provider.
    Used for offline testing, integration suites, and fallback development.
    """
    NAME = "mock"

    BASE_ASSETS: Dict[str, Dict] = {
        "BTC": {"name": "Bitcoin", "slug": "bitcoin", "provider_id": "bitcoin", "base_price": 65000.0, "rank": 1, "mcap": 1280000000000.0, "supply": 19700000.0},
        "ETH": {"name": "Ethereum", "slug": "ethereum", "provider_id": "ethereum", "base_price": 3500.0, "rank": 2, "mcap": 420000000000.0, "supply": 120000000.0},
        "SOL": {"name": "Solana", "slug": "solana", "provider_id": "solana", "base_price": 150.0, "rank": 3, "mcap": 68000000000.0, "supply": 460000000.0},
        "BNB": {"name": "BNB", "slug": "binancecoin", "provider_id": "binancecoin", "base_price": 580.0, "rank": 4, "mcap": 89000000000.0, "supply": 153000000.0},
        "XRP": {"name": "XRP", "slug": "ripple", "provider_id": "ripple", "base_price": 0.58, "rank": 5, "mcap": 32000000000.0, "supply": 55000000000.0},
        "ADA": {"name": "Cardano", "slug": "cardano", "provider_id": "cardano", "base_price": 0.42, "rank": 6, "mcap": 15000000000.0, "supply": 35000000000.0},
        "AVAX": {"name": "Avalanche", "slug": "avalanche-2", "provider_id": "avalanche-2", "base_price": 28.5, "rank": 7, "mcap": 11000000000.0, "supply": 395000000.0},
        "DOT": {"name": "Polkadot", "slug": "polkadot", "provider_id": "polkadot", "base_price": 6.8, "rank": 8, "mcap": 9500000000.0, "supply": 1400000000.0},
        "LINK": {"name": "Chainlink", "slug": "chainlink", "provider_id": "chainlink", "base_price": 14.2, "rank": 9, "mcap": 8600000000.0, "supply": 608000000.0},
        "MATIC": {"name": "Polygon", "slug": "matic-network", "provider_id": "matic-network", "base_price": 0.52, "rank": 10, "mcap": 5100000000.0, "supply": 9800000000.0},
    }

    @property
    def name(self) -> str:
        return self.NAME

    def _resolve_symbol(self, symbol_or_id: str) -> Optional[str]:
        cleaned = symbol_or_id.upper().strip()
        if cleaned in self.BASE_ASSETS:
            return cleaned
        # Check slugs
        lower = symbol_or_id.lower().strip()
        for sym, data in self.BASE_ASSETS.items():
            if data["slug"] == lower or data["provider_id"] == lower:
                return sym
        return None

    def _calculate_price_factor(self, symbol: str, timestamp: datetime) -> float:
        """Deterministic pseudo-random wave fluctuation based on symbol and timestamp."""
        seed = int(hashlib.md5(f"{symbol}:{timestamp.strftime('%Y-%m-%d %H')}".encode()).hexdigest()[:8], 16)
        wave = math.sin(seed % 360) * 0.03
        return 1.0 + wave

    async def get_asset(self, symbol_or_id: str) -> Optional[NormalizedAsset]:
        sym = self._resolve_symbol(symbol_or_id)
        if not sym:
            return None
        data = self.BASE_ASSETS[sym]
        return NormalizedAsset(
            symbol=sym,
            name=data["name"],
            slug=data["slug"],
            provider_id=data["provider_id"],
            asset_type="crypto",
            status="active",
            is_active=True,
            rank=data["rank"],
            metadata={"source": "mock", "circulating_supply": data["supply"]},
        )

    async def get_current_price(self, symbol: str) -> NormalizedPrice:
        sym = self._resolve_symbol(symbol)
        if not sym:
            raise AssetNotFoundException(symbol, provider=self.NAME)

        data = self.BASE_ASSETS[sym]
        now = datetime.now(timezone.utc)
        factor = self._calculate_price_factor(sym, now)
        current_price = round(data["base_price"] * factor, 4 if data["base_price"] < 10 else 2)
        pct_change = round((factor - 1.0) * 100, 2)
        price_change = round(current_price * (pct_change / 100), 4)

        return NormalizedPrice(
            symbol=sym,
            price=current_price,
            price_change_24h=price_change,
            price_change_percentage_24h=pct_change,
            high_24h=round(current_price * 1.04, 2),
            low_24h=round(current_price * 0.96, 2),
            volume_24h=round(data["mcap"] * 0.08, 2),
            source_timestamp=now,
            provider=self.NAME,
        )

    async def get_market_snapshot(self, symbol: str) -> NormalizedSnapshot:
        sym = self._resolve_symbol(symbol)
        if not sym:
            raise AssetNotFoundException(symbol, provider=self.NAME)

        data = self.BASE_ASSETS[sym]
        price_data = await self.get_current_price(sym)

        return NormalizedSnapshot(
            symbol=sym,
            name=data["name"],
            price=price_data.price,
            market_cap=round(price_data.price * data["supply"], 2),
            volume_24h=price_data.volume_24h,
            price_change_24h=price_data.price_change_24h,
            price_change_percentage_24h=price_data.price_change_percentage_24h,
            high_24h=price_data.high_24h,
            low_24h=price_data.low_24h,
            circulating_supply=data["supply"],
            total_supply=data["supply"],
            source_timestamp=price_data.source_timestamp,
            provider=self.NAME,
        )

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        limit: int = 100,
    ) -> List[NormalizedCandle]:
        sym = self._resolve_symbol(symbol)
        if not sym:
            raise AssetNotFoundException(symbol, provider=self.NAME)

        data = self.BASE_ASSETS[sym]
        now = datetime.now(timezone.utc)
        candles: List[NormalizedCandle] = []

        step_minutes = timeframe.minutes
        for i in range(limit - 1, -1, -1):
            ts = now - timedelta(minutes=step_minutes * (i + 1))
            factor = self._calculate_price_factor(sym, ts)
            base = data["base_price"] * factor

            open_p = round(base * (1 + math.sin(i) * 0.005), 2)
            close_p = round(base * (1 + math.cos(i) * 0.005), 2)
            high_p = round(max(open_p, close_p) * 1.015, 2)
            low_p = round(min(open_p, close_p) * 0.985, 2)
            vol = round(base * 1200 * (1 + (i % 5) * 0.2), 2)

            candles.append(
                NormalizedCandle(
                    timestamp=ts,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=vol,
                    timeframe=timeframe,
                    provider=self.NAME,
                )
            )

        return candles

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        start_time: datetime,
        end_time: datetime,
    ) -> List[NormalizedCandle]:
        sym = self._resolve_symbol(symbol)
        if not sym:
            raise AssetNotFoundException(symbol, provider=self.NAME)

        data = self.BASE_ASSETS[sym]
        step_minutes = timeframe.minutes
        candles: List[NormalizedCandle] = []

        current_ts = start_time
        idx = 0
        while current_ts <= end_time:
            factor = self._calculate_price_factor(sym, current_ts)
            base = data["base_price"] * factor

            open_p = round(base * (1 + math.sin(idx) * 0.005), 2)
            close_p = round(base * (1 + math.cos(idx) * 0.005), 2)
            high_p = round(max(open_p, close_p) * 1.015, 2)
            low_p = round(min(open_p, close_p) * 0.985, 2)
            vol = round(base * 1000 * (1 + (idx % 7) * 0.1), 2)

            candles.append(
                NormalizedCandle(
                    timestamp=current_ts,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=vol,
                    timeframe=timeframe,
                    provider=self.NAME,
                )
            )
            current_ts += timedelta(minutes=step_minutes)
            idx += 1
            if len(candles) >= 1000:
                break

        return candles

    async def get_supported_assets(self) -> List[NormalizedAsset]:
        results: List[NormalizedAsset] = []
        for sym, data in self.BASE_ASSETS.items():
            results.append(
                NormalizedAsset(
                    symbol=sym,
                    name=data["name"],
                    slug=data["slug"],
                    provider_id=data["provider_id"],
                    asset_type="crypto",
                    status="active",
                    is_active=True,
                    rank=data["rank"],
                    metadata={"source": "mock", "circulating_supply": data["supply"]},
                )
            )
        return results

    async def health_check(self) -> bool:
        return True

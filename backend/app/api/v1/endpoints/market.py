from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_authenticated_user
from app.schemas.market import (
    TimeframeEnum,
    AssetResponse,
    PriceResponse,
    MarketSnapshotResponse,
    OHLCVResponse,
)
from app.services.market.service import market_service
from app.services.market.base import AssetNotFoundException, MarketDataException

router = APIRouter()

@router.get(
    "/assets",
    response_model=List[AssetResponse],
    status_code=status.HTTP_200_OK,
    summary="List supported cryptocurrency assets",
)
def list_assets(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=250, description="Items per page"),
    status_filter: Optional[str] = Query("active", alias="status", description="Filter by asset status"),
    search: Optional[str] = Query(None, description="Search by symbol or asset name"),
    db: Session = Depends(get_db),
):
    """
    Retrieve registered cryptocurrency assets from the internal asset registry.
    """
    assets, _ = market_service.list_assets(
        db=db, skip=skip, limit=limit, status=status_filter, search=search
    )
    return assets

@router.get(
    "/assets/{asset_id}",
    response_model=AssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get cryptocurrency asset metadata",
)
def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed metadata for a specific cryptocurrency asset by ID or symbol.
    """
    asset = market_service.resolve_asset(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency asset '{asset_id}' not found.",
        )
    return AssetResponse.model_validate(asset)

@router.get(
    "/assets/{asset_id}/price",
    response_model=PriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get normalized real-time asset price and 24h metrics",
)
async def get_current_price(
    asset_id: str,
    db: Session = Depends(get_db),
):
    """
    Fetch normalized current price, 24-hour change, and observable freshness metadata.
    Data is served from cache when warm and refreshed transparently from provider upon cache expiration.
    """
    try:
        return await market_service.get_current_price(db, asset_id)
    except AssetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.message))
    except MarketDataException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.message))

@router.get(
    "/assets/{asset_id}/snapshot",
    response_model=MarketSnapshotResponse,
    status_code=status.HTTP_200_OK,
    summary="Get comprehensive 24h market snapshot",
)
async def get_market_snapshot(
    asset_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve a comprehensive 24-hour market snapshot including market cap, 24h high/low, volume, and supplies.
    """
    try:
        return await market_service.get_market_snapshot(db, asset_id)
    except AssetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.message))
    except MarketDataException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.message))

@router.get(
    "/assets/{asset_id}/ohlcv",
    response_model=OHLCVResponse,
    status_code=status.HTTP_200_OK,
    summary="Get latest OHLCV candlesticks for specified timeframe",
)
async def get_ohlcv(
    asset_id: str,
    timeframe: TimeframeEnum = Query(TimeframeEnum.ONE_HOUR, description="Candlestick timeframe interval"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve the latest normalized OHLCV candlesticks for an asset.
    Supported timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w.
    """
    try:
        return await market_service.get_ohlcv(db, asset_id, timeframe=timeframe, limit=limit)
    except AssetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.message))
    except MarketDataException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.message))

@router.get(
    "/assets/{asset_id}/historical",
    response_model=OHLCVResponse,
    status_code=status.HTTP_200_OK,
    summary="Get historical OHLCV candlestick series within a time range",
)
async def get_historical_ohlcv(
    asset_id: str,
    timeframe: TimeframeEnum = Query(TimeframeEnum.ONE_DAY, description="Candlestick timeframe interval"),
    start_time: Optional[datetime] = Query(None, description="Start timestamp (ISO 8601)"),
    end_time: Optional[datetime] = Query(None, description="End timestamp (ISO 8601)"),
    limit: int = Query(250, ge=1, le=1000, description="Max number of historical candles to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve historical OHLCV candlestick series between start_time and end_time.
    Guarantees chronological ordering and zero duplicates.
    """
    now = datetime.now(timezone.utc)
    effective_end = end_time or now
    effective_start = start_time or (effective_end - timedelta(days=30))

    if effective_start >= effective_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be earlier than end_time.",
        )

    try:
        return await market_service.get_historical_ohlcv(
            db=db,
            identifier=asset_id,
            timeframe=timeframe,
            start_time=effective_start,
            end_time=effective_end,
            limit=limit,
        )
    except AssetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.message))
    except MarketDataException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.message))

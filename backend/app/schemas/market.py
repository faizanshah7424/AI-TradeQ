from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TimeframeEnum(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"

    @property
    def minutes(self) -> int:
        mapping = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "30m": 30,
            "1h": 60,
            "4h": 240,
            "1d": 1440,
            "1w": 10080,
        }
        return mapping.get(self.value, 60)

    @property
    def seconds(self) -> int:
        return self.minutes * 60

class FreshnessMetadata(BaseModel):
    source_timestamp: datetime = Field(..., description="Timestamp when data was generated at provider")
    ingested_at: datetime = Field(..., description="Timestamp when data was received by AI TradeQ")
    cached_at: Optional[datetime] = Field(None, description="Timestamp when cached (if served from cache)")
    age_seconds: float = Field(..., description="Age of data in seconds relative to current time")
    is_stale: bool = Field(..., description="Flag indicating if data exceeds freshness threshold")
    provider: str = Field(..., description="Originating data provider identifier")

class AssetResponse(BaseModel):
    id: str
    symbol: str
    name: str
    slug: str
    provider_id: str
    asset_type: str = "crypto"
    status: str = "active"
    is_active: bool = True
    rank: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PriceResponse(BaseModel):
    symbol: str
    asset_id: str
    price: float = Field(..., description="Current asset price in USD")
    price_change_24h: Optional[float] = Field(None, description="24-hour price change amount in USD")
    price_change_percentage_24h: Optional[float] = Field(None, description="24-hour percentage price change")
    high_24h: Optional[float] = Field(None, description="24-hour high price in USD")
    low_24h: Optional[float] = Field(None, description="24-hour low price in USD")
    volume_24h: Optional[float] = Field(None, description="24-hour trading volume in USD")
    freshness: FreshnessMetadata

class MarketSnapshotResponse(BaseModel):
    id: Optional[str] = None
    asset_id: str
    symbol: str
    name: str
    price: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    data_timestamp: datetime
    freshness: FreshnessMetadata

    class Config:
        from_attributes = True

class CandleResponse(BaseModel):
    timestamp: datetime = Field(..., description="Opening timestamp of the candlestick")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price during period")
    low: float = Field(..., description="Lowest price during period")
    close: float = Field(..., description="Closing price")
    volume: float = Field(..., description="Volume traded during period")

    class Config:
        from_attributes = True

class OHLCVResponse(BaseModel):
    symbol: str
    asset_id: str
    timeframe: TimeframeEnum
    count: int
    candles: List[CandleResponse]
    freshness: FreshnessMetadata

    class Config:
        from_attributes = True

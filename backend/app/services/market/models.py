from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from app.schemas.market import TimeframeEnum

@dataclass
class NormalizedAsset:
    symbol: str
    name: str
    slug: str
    provider_id: str
    asset_type: str = "crypto"
    status: str = "active"
    is_active: bool = True
    rank: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NormalizedPrice:
    symbol: str
    price: float
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    source_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str = "unknown"

@dataclass
class NormalizedSnapshot:
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
    source_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str = "unknown"

@dataclass
class NormalizedCandle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: TimeframeEnum
    provider: str = "unknown"

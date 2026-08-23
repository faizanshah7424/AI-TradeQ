from datetime import datetime, timezone
from typing import Optional
from app.core.config import settings
from app.schemas.market import FreshnessMetadata, TimeframeEnum

class FreshnessPolicy:
    """
    Evaluates market data age and staleness against configurable freshness policies.
    """

    @staticmethod
    def get_max_staleness(data_type: str, timeframe: Optional[TimeframeEnum] = None) -> float:
        if data_type == "price":
            return float(getattr(settings, "MARKET_DATA_MAX_STALENESS_PRICE_SECONDS", 60))
        elif data_type == "snapshot":
            return float(getattr(settings, "MARKET_DATA_MAX_STALENESS_SNAPSHOT_SECONDS", 300))
        elif data_type == "ohlcv":
            if timeframe:
                # Max staleness for OHLCV is 2x candle timeframe length
                return float(timeframe.seconds * 2)
            return 3600.0
        return 300.0

    @classmethod
    def evaluate_freshness(
        cls,
        source_timestamp: datetime,
        ingested_at: datetime,
        provider: str,
        data_type: str = "price",
        timeframe: Optional[TimeframeEnum] = None,
        cached_at: Optional[datetime] = None,
    ) -> FreshnessMetadata:
        now = datetime.now(timezone.utc)
        
        # Ensure UTC timezone awareness
        if source_timestamp.tzinfo is None:
            source_ts = source_timestamp.replace(tzinfo=timezone.utc)
        else:
            source_ts = source_timestamp

        if ingested_at.tzinfo is None:
            ingested_ts = ingested_at.replace(tzinfo=timezone.utc)
        else:
            ingested_ts = ingested_at

        age_seconds = max(0.0, (now - source_ts).total_seconds())
        max_staleness = cls.get_max_staleness(data_type, timeframe)
        is_stale = age_seconds > max_staleness

        return FreshnessMetadata(
            source_timestamp=source_ts,
            ingested_at=ingested_ts,
            cached_at=cached_at,
            age_seconds=round(age_seconds, 2),
            is_stale=is_stale,
            provider=provider,
        )

freshness_policy = FreshnessPolicy()

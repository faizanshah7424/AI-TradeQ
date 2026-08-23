import logging
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional, List, Dict
from app.services.market.models import (
    NormalizedPrice,
    NormalizedSnapshot,
    NormalizedCandle,
)

logger = logging.getLogger("market.validator")

class MarketDataValidator:
    """
    Validates external market data integrity before ingestion, caching, or persistence.
    Protects downstream AI and prediction systems from corrupted or anomalous data.
    """

    @staticmethod
    def validate_price(price: NormalizedPrice) -> Tuple[bool, Optional[str]]:
        if price.price is None or price.price <= 0:
            return False, f"Invalid price value: {price.price} (must be > 0)"
        
        now = datetime.now(timezone.utc)
        if price.source_timestamp > now + timedelta(minutes=5):
            return False, f"Price source timestamp is in the future: {price.source_timestamp}"

        if price.high_24h is not None and price.low_24h is not None:
            if price.high_24h < price.low_24h:
                return False, f"24h High ({price.high_24h}) cannot be lower than 24h Low ({price.low_24h})"

        return True, None

    @staticmethod
    def validate_snapshot(snapshot: NormalizedSnapshot) -> Tuple[bool, Optional[str]]:
        if snapshot.price is None or snapshot.price <= 0:
            return False, f"Invalid snapshot price: {snapshot.price} (must be > 0)"

        if snapshot.volume_24h is not None and snapshot.volume_24h < 0:
            return False, f"24h volume cannot be negative: {snapshot.volume_24h}"

        if snapshot.high_24h is not None and snapshot.low_24h is not None:
            if snapshot.high_24h < snapshot.low_24h:
                return False, f"24h High ({snapshot.high_24h}) is less than 24h Low ({snapshot.low_24h})"

        now = datetime.now(timezone.utc)
        if snapshot.source_timestamp > now + timedelta(minutes=5):
            return False, f"Snapshot timestamp is in the future: {snapshot.source_timestamp}"

        return True, None

    @staticmethod
    def validate_candle(candle: NormalizedCandle) -> Tuple[bool, Optional[str]]:
        if candle.open <= 0 or candle.high <= 0 or candle.low <= 0 or candle.close <= 0:
            return False, f"Candle OHLC values must be positive: O={candle.open}, H={candle.high}, L={candle.low}, C={candle.close}"

        if candle.volume < 0:
            return False, f"Candle volume cannot be negative: {candle.volume}"

        # High must be the maximum value
        if candle.high < candle.open or candle.high < candle.close or candle.high < candle.low:
            return False, f"Candle High ({candle.high}) is lower than Open ({candle.open}), Close ({candle.close}), or Low ({candle.low})"

        # Low must be the minimum value
        if candle.low > candle.open or candle.low > candle.close or candle.low > candle.high:
            return False, f"Candle Low ({candle.low}) is higher than Open ({candle.open}), Close ({candle.close}), or High ({candle.high})"

        now = datetime.now(timezone.utc)
        if candle.timestamp > now + timedelta(minutes=5):
            return False, f"Candle timestamp is in the future: {candle.timestamp}"

        return True, None

    @classmethod
    def sanitize_candles(cls, candles: List[NormalizedCandle]) -> List[NormalizedCandle]:
        """
        Filter out invalid candles, deduplicate by timestamp, and enforce chronological sorting.
        """
        valid_candles: List[NormalizedCandle] = []
        seen_timestamps = set()

        for c in candles:
            is_valid, error = cls.validate_candle(c)
            if not is_valid:
                logger.warning("Dropping invalid candle: %s | Error: %s", c, error)
                continue
            
            ts_key = (c.timeframe.value, c.timestamp.isoformat())
            if ts_key in seen_timestamps:
                logger.debug("Dropping duplicate candle for timestamp %s", c.timestamp)
                continue

            seen_timestamps.add(ts_key)
            valid_candles.append(c)

        # Sort strictly by timestamp ascending
        valid_candles.sort(key=lambda x: x.timestamp)
        return valid_candles

validator = MarketDataValidator()

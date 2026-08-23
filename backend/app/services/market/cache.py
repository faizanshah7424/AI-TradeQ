import time
import json
import logging
from threading import Lock
from typing import Optional, Any, Dict
from datetime import datetime, timezone
from app.core.config import settings

logger = logging.getLogger("market.cache")

class MarketDataCache:
    """
    High-performance, deterministic caching layer for market intelligence.
    Supports in-memory TTL caching with seamless Redis upgradability.
    """

    def __init__(self):
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    @staticmethod
    def price_key(symbol: str) -> str:
        return f"market:v1:price:{symbol.upper()}"

    @staticmethod
    def snapshot_key(symbol: str) -> str:
        return f"market:v1:snapshot:{symbol.upper()}"

    @staticmethod
    def ohlcv_key(symbol: str, timeframe: str, limit: int) -> str:
        return f"market:v1:ohlcv:{symbol.upper()}:{timeframe}:{limit}"

    @staticmethod
    def asset_key(identifier: str) -> str:
        return f"market:v1:asset:{identifier.upper()}"

    @staticmethod
    def assets_list_key() -> str:
        return "market:v1:assets:list"

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._lock:
            entry = self._memory_store.get(key)
            if not entry:
                return None

            if entry["expires_at"] < now:
                # Expired
                self._memory_store.pop(key, None)
                return None

            return entry["data"]

    def set(self, key: str, data: Any, ttl_seconds: int):
        now = time.time()
        with self._lock:
            self._memory_store[key] = {
                "data": data,
                "cached_at": datetime.now(timezone.utc),
                "expires_at": now + ttl_seconds,
            }

    def get_with_cached_at(self, key: str) -> Tuple_Opt:
        now = time.time()
        with self._lock:
            entry = self._memory_store.get(key)
            if not entry:
                return None, None

            if entry["expires_at"] < now:
                self._memory_store.pop(key, None)
                return None, None

            return entry["data"], entry.get("cached_at")

    def delete(self, key: str):
        with self._lock:
            self._memory_store.pop(key, None)

    def clear(self):
        with self._lock:
            self._memory_store.clear()

Tuple_Opt = tuple[Optional[Any], Optional[datetime]]
market_cache = MarketDataCache()

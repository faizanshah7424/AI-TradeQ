import time
import pytest
from app.services.market.cache import MarketDataCache

def test_cache_set_get_and_expiration():
    cache = MarketDataCache()
    key = cache.price_key("BTC")
    assert key == "market:v1:price:BTC"

    # Set data with short TTL
    cache.set(key, {"price": 65000.0}, ttl_seconds=1)
    cached_val = cache.get(key)
    assert cached_val == {"price": 65000.0}

    # Expire
    time.sleep(1.1)
    expired_val = cache.get(key)
    assert expired_val is None

def test_cache_delete_and_clear():
    cache = MarketDataCache()
    cache.set("key1", "val1", ttl_seconds=60)
    cache.set("key2", "val2", ttl_seconds=60)

    assert cache.get("key1") == "val1"
    cache.delete("key1")
    assert cache.get("key1") is None
    assert cache.get("key2") == "val2"

    cache.clear()
    assert cache.get("key2") is None

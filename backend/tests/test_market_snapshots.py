import pytest
from datetime import datetime, timezone, timedelta
from fastapi import status
from app.services.market.models import NormalizedSnapshot
from app.services.market.validator import validator

def test_market_snapshot_api(client, db_session):
    response = client.get("/api/v1/market/assets/BTC/snapshot")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "BTC"
    assert data["price"] > 0
    assert data["market_cap"] > 0
    assert "freshness" in data
    assert data["freshness"]["is_stale"] is False
    assert data["freshness"]["age_seconds"] >= 0

def test_snapshot_validator_rules():
    # Valid snapshot
    valid_s = NormalizedSnapshot(
        symbol="BTC",
        name="Bitcoin",
        price=65000.0,
        market_cap=1200000000000.0,
        volume_24h=25000000000.0,
        high_24h=66000.0,
        low_24h=64000.0,
        source_timestamp=datetime.now(timezone.utc),
    )
    is_valid, error = validator.validate_snapshot(valid_s)
    assert is_valid is True
    assert error is None

    # Invalid price <= 0
    invalid_price = NormalizedSnapshot(
        symbol="BTC",
        name="Bitcoin",
        price=-10.0,
        source_timestamp=datetime.now(timezone.utc),
    )
    is_valid, error = validator.validate_snapshot(invalid_price)
    assert is_valid is False
    assert "must be > 0" in error

    # Invalid high < low
    invalid_high_low = NormalizedSnapshot(
        symbol="BTC",
        name="Bitcoin",
        price=65000.0,
        high_24h=60000.0,
        low_24h=64000.0,
        source_timestamp=datetime.now(timezone.utc),
    )
    is_valid, error = validator.validate_snapshot(invalid_high_low)
    assert is_valid is False
    assert "less than 24h Low" in error

import pytest
from datetime import datetime, timezone
from fastapi import status
from app.schemas.market import TimeframeEnum
from app.services.market.models import NormalizedCandle
from app.services.market.validator import validator

def test_get_ohlcv_api_timeframes(client, db_session):
    for tf in ["1m", "5m", "15m", "1h", "4h", "1d"]:
        response = client.get(f"/api/v1/market/assets/BTC/ohlcv?timeframe={tf}&limit=20")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["symbol"] == "BTC"
        assert data["timeframe"] == tf
        assert len(data["candles"]) == 20
        # Verify chronological order
        timestamps = [c["timestamp"] for c in data["candles"]]
        assert timestamps == sorted(timestamps)

def test_ohlcv_validator_anomalies():
    now = datetime.now(timezone.utc)
    # Valid candle
    valid_c = NormalizedCandle(
        timestamp=now,
        open=100.0,
        high=110.0,
        low=95.0,
        close=105.0,
        volume=500.0,
        timeframe=TimeframeEnum.ONE_HOUR,
    )
    is_valid, error = validator.validate_candle(valid_c)
    assert is_valid is True

    # High lower than Open
    bad_high = NormalizedCandle(
        timestamp=now,
        open=100.0,
        high=90.0,
        low=85.0,
        close=88.0,
        volume=500.0,
        timeframe=TimeframeEnum.ONE_HOUR,
    )
    is_valid, error = validator.validate_candle(bad_high)
    assert is_valid is False
    assert "High" in error

    # Low higher than Close
    bad_low = NormalizedCandle(
        timestamp=now,
        open=100.0,
        high=110.0,
        low=102.0,
        close=95.0,
        volume=500.0,
        timeframe=TimeframeEnum.ONE_HOUR,
    )
    is_valid, error = validator.validate_candle(bad_low)
    assert is_valid is False
    assert "Low" in error

def test_historical_ohlcv_range_query(client, db_session):
    response = client.get("/api/v1/market/assets/ETH/historical?timeframe=1d&limit=30")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "ETH"
    assert len(data["candles"]) > 0

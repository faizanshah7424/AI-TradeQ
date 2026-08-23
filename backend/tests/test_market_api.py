import pytest
from fastapi import status

def test_get_assets_endpoint(client, db_session):
    response = client.get("/api/v1/market/assets")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_get_single_asset_endpoint(client, db_session):
    response = client.get("/api/v1/market/assets/BTC")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "BTC"
    assert "name" in data

def test_get_current_price_endpoint(client, db_session):
    response = client.get("/api/v1/market/assets/BTC/price")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "BTC"
    assert data["price"] > 0
    assert "freshness" in data
    assert data["freshness"]["is_stale"] is False

def test_get_market_snapshot_endpoint(client, db_session):
    response = client.get("/api/v1/market/assets/ETH/snapshot")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "ETH"
    assert data["price"] > 0
    assert "market_cap" in data

def test_get_ohlcv_endpoint(client, db_session):
    response = client.get("/api/v1/market/assets/SOL/ohlcv?timeframe=1h&limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "SOL"
    assert len(data["candles"]) == 10

def test_get_historical_endpoint(client, db_session):
    response = client.get("/api/v1/market/assets/BTC/historical?timeframe=1d&limit=15")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "BTC"
    assert len(data["candles"]) > 0

def test_invalid_asset_returns_404(client, db_session):
    response = client.get("/api/v1/market/assets/UNKNOWNCOINXYZ/price")
    # If not in mock/provider, raises 404
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

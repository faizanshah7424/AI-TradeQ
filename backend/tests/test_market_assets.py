import pytest
from fastapi import status
from app.models.market import CryptoAsset
from app.services.market.service import market_service

def test_asset_creation_and_retrieval(client, db_session):
    asset = market_service.get_or_create_asset(
        db=db_session,
        symbol="BTC",
        name="Bitcoin",
        slug="bitcoin",
        provider_id="bitcoin",
    )
    assert asset.id is not None
    assert asset.symbol == "BTC"
    assert asset.name == "Bitcoin"

    # API lookup by symbol
    response = client.get("/api/v1/market/assets/BTC")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "BTC"
    assert data["name"] == "Bitcoin"
    assert data["id"] == asset.id

def test_list_assets_with_search_and_pagination(client, db_session):
    market_service.get_or_create_asset(db_session, symbol="ETH", name="Ethereum", slug="ethereum", provider_id="ethereum")
    market_service.get_or_create_asset(db_session, symbol="SOL", name="Solana", slug="solana", provider_id="solana")

    response = client.get("/api/v1/market/assets?limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2

    # Search filter
    search_res = client.get("/api/v1/market/assets?search=solana")
    assert search_res.status_code == status.HTTP_200_OK
    search_data = search_res.json()
    assert len(search_data) >= 1
    assert any(a["symbol"] == "SOL" for a in search_data)

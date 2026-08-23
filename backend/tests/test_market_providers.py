import pytest
from datetime import datetime, timezone
from app.schemas.market import TimeframeEnum
from app.services.market.providers.mock_provider import MockMarketDataProvider
from app.services.market.providers.coingecko import CoinGeckoProvider
from app.services.market.providers.binance import BinanceProvider

@pytest.mark.asyncio
async def test_mock_provider_contracts():
    provider = MockMarketDataProvider()
    assert provider.name == "mock"

    # Price
    price = await provider.get_current_price("BTC")
    assert price.symbol == "BTC"
    assert price.price > 0
    assert price.provider == "mock"

    # Snapshot
    snapshot = await provider.get_market_snapshot("ETH")
    assert snapshot.symbol == "ETH"
    assert snapshot.price > 0
    assert snapshot.market_cap > 0

    # OHLCV
    candles = await provider.get_ohlcv("SOL", TimeframeEnum.ONE_HOUR, limit=25)
    assert len(candles) == 25
    assert candles[0].timeframe == TimeframeEnum.ONE_HOUR

    # Supported Assets
    assets = await provider.get_supported_assets()
    assert len(assets) >= 10
    assert any(a.symbol == "BTC" for a in assets)

@pytest.mark.asyncio
async def test_provider_url_and_headers_configuration():
    cg = CoinGeckoProvider()
    assert "coingecko.com" in cg.base_url
    assert cg.name == "coingecko"

    bn = BinanceProvider()
    assert "binance.com" in bn.base_url
    assert bn.name == "binance"

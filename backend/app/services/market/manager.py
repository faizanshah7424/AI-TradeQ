import logging
from datetime import datetime
from typing import Dict, List, Optional
from app.core.config import settings
from app.schemas.market import TimeframeEnum
from app.services.market.base import (
    BaseMarketDataProvider,
    MarketDataException,
    AssetNotFoundException,
)
from app.services.market.models import (
    NormalizedAsset,
    NormalizedPrice,
    NormalizedSnapshot,
    NormalizedCandle,
)
from app.services.market.resilience import resilience_manager
from app.services.market.providers.mock_provider import MockMarketDataProvider
from app.services.market.providers.coingecko import CoinGeckoProvider
from app.services.market.providers.binance import BinanceProvider

logger = logging.getLogger("market.manager")

class MarketDataProviderManager:
    """
    Orchestrates market data providers with automatic multi-provider fallback.
    """

    def __init__(self):
        self._providers: Dict[str, BaseMarketDataProvider] = {}
        # Register standard providers
        self.register_provider(MockMarketDataProvider())
        self.register_provider(CoinGeckoProvider())
        self.register_provider(BinanceProvider())

    def register_provider(self, provider: BaseMarketDataProvider):
        self._providers[provider.name.lower()] = provider

    def get_provider(self, name: str) -> BaseMarketDataProvider:
        key = name.lower()
        if key not in self._providers:
            logger.warning("Provider '%s' not registered. Falling back to 'mock'", name)
            return self._providers["mock"]
        return self._providers[key]

    @property
    def primary_provider(self) -> BaseMarketDataProvider:
        name = getattr(settings, "PRIMARY_MARKET_DATA_PROVIDER", "mock")
        return self.get_provider(name)

    @property
    def fallback_provider(self) -> BaseMarketDataProvider:
        name = getattr(settings, "FALLBACK_MARKET_DATA_PROVIDER", "mock")
        return self.get_provider(name)

    async def get_current_price(self, symbol: str) -> NormalizedPrice:
        primary = self.primary_provider
        fallback = self.fallback_provider

        try:
            return await resilience_manager.execute_with_resilience(
                primary.name,
                lambda: primary.get_current_price(symbol),
                max_retries=getattr(settings, "MARKET_DATA_MAX_RETRIES", 3),
            )
        except AssetNotFoundException:
            raise
        except Exception as e:
            if primary.name == fallback.name:
                raise
            logger.warning(
                "Primary provider '%s' failed for price '%s': %s. Falling back to '%s'",
                primary.name, symbol, str(e), fallback.name
            )
            return await resilience_manager.execute_with_resilience(
                fallback.name,
                lambda: fallback.get_current_price(symbol),
                max_retries=getattr(settings, "MARKET_DATA_MAX_RETRIES", 3),
            )

    async def get_market_snapshot(self, symbol: str) -> NormalizedSnapshot:
        primary = self.primary_provider
        fallback = self.fallback_provider

        try:
            return await resilience_manager.execute_with_resilience(
                primary.name,
                lambda: primary.get_market_snapshot(symbol),
                max_retries=getattr(settings, "MARKET_DATA_MAX_RETRIES", 3),
            )
        except AssetNotFoundException:
            raise
        except Exception as e:
            if primary.name == fallback.name:
                raise
            logger.warning(
                "Primary provider '%s' failed for snapshot '%s': %s. Falling back to '%s'",
                primary.name, symbol, str(e), fallback.name
            )
            return await resilience_manager.execute_with_resilience(
                fallback.name,
                lambda: fallback.get_market_snapshot(symbol),
                max_retries=getattr(settings, "MARKET_DATA_MAX_RETRIES", 3),
            )

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        limit: int = 100,
    ) -> List[NormalizedCandle]:
        primary = self.primary_provider
        fallback = self.fallback_provider

        try:
            return await resilience_manager.execute_with_resilience(
                primary.name,
                lambda: primary.get_ohlcv(symbol, timeframe, limit),
                max_retries=getattr(settings, "MARKET_DATA_MAX_RETRIES", 3),
            )
        except AssetNotFoundException:
            raise
        except Exception as e:
            if primary.name == fallback.name:
                raise
            logger.warning(
                "Primary provider '%s' failed for OHLCV '%s' %s: %s. Falling back to '%s'",
                primary.name, symbol, timeframe.value, str(e), fallback.name
            )
            return await resilience_manager.execute_with_resilience(
                fallback.name,
                lambda: fallback.get_ohlcv(symbol, timeframe, limit),
                max_retries=getattr(settings, "MARKET_DATA_MAX_RETRIES", 3),
            )

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        start_time: datetime,
        end_time: datetime,
    ) -> List[NormalizedCandle]:
        primary = self.primary_provider
        fallback = self.fallback_provider

        try:
            return await resilience_manager.execute_with_resilience(
                primary.name,
                lambda: primary.get_historical_data(symbol, timeframe, start_time, end_time),
                max_retries=getattr(settings, "MARKET_DATA_MAX_RETRIES", 3),
            )
        except AssetNotFoundException:
            raise
        except Exception as e:
            if primary.name == fallback.name:
                raise
            logger.warning(
                "Primary provider '%s' failed for historical '%s': %s. Falling back to '%s'",
                primary.name, symbol, str(e), fallback.name
            )
            return await resilience_manager.execute_with_resilience(
                fallback.name,
                lambda: fallback.get_historical_data(symbol, timeframe, start_time, end_time),
                max_retries=getattr(settings, "MARKET_DATA_MAX_RETRIES", 3),
            )

    async def get_supported_assets(self) -> List[NormalizedAsset]:
        return await self.primary_provider.get_supported_assets()

provider_manager = MarketDataProviderManager()

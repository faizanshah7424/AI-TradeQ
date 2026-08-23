from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List
from app.schemas.market import TimeframeEnum
from app.services.market.models import (
    NormalizedAsset,
    NormalizedPrice,
    NormalizedSnapshot,
    NormalizedCandle,
)

class MarketDataException(Exception):
    """Base exception for all market data operations."""
    def __init__(self, message: str, provider: str = "unknown", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code

class ProviderConnectionException(MarketDataException):
    """Network connection or DNS failure communicating with external provider."""
    pass

class ProviderTimeoutException(MarketDataException):
    """Request timeout communicating with external provider."""
    pass

class ProviderRateLimitException(MarketDataException):
    """Rate limit exceeded at external provider (HTTP 429)."""
    def __init__(self, message: str, provider: str = "unknown", retry_after_seconds: Optional[int] = None):
        super().__init__(message, provider=provider, status_code=429)
        self.retry_after_seconds = retry_after_seconds

class ProviderResponseException(MarketDataException):
    """Malformed or unexpected HTTP response from external provider."""
    pass

class AssetNotFoundException(MarketDataException):
    """Requested cryptocurrency asset is not found or unsupported."""
    def __init__(self, symbol_or_id: str, provider: str = "unknown"):
        super().__init__(f"Asset '{symbol_or_id}' was not found at provider '{provider}'.", provider=provider, status_code=404)

class BaseMarketDataProvider(ABC):
    """
    Abstract interface for all external and internal market data providers.
    Ensures provider-agnostic business logic throughout AI TradeQ.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider unique identifier (e.g. 'coingecko', 'binance', 'mock')."""
        pass

    @abstractmethod
    async def get_asset(self, symbol_or_id: str) -> Optional[NormalizedAsset]:
        """Fetch asset metadata from provider."""
        pass

    @abstractmethod
    async def get_current_price(self, symbol: str) -> NormalizedPrice:
        """Fetch real-time current price and 24h ticker metrics."""
        pass

    @abstractmethod
    async def get_market_snapshot(self, symbol: str) -> NormalizedSnapshot:
        """Fetch comprehensive market snapshot (price, market cap, 24h stats, volume, supply)."""
        pass

    @abstractmethod
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        limit: int = 100,
    ) -> List[NormalizedCandle]:
        """Fetch latest OHLCV candlesticks for the specified timeframe."""
        pass

    @abstractmethod
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        start_time: datetime,
        end_time: datetime,
    ) -> List[NormalizedCandle]:
        """Fetch chronological historical candlestick series between start and end timestamps."""
        pass

    @abstractmethod
    async def get_supported_assets(self) -> List[NormalizedAsset]:
        """Fetch list of all supported assets from provider."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Perform a liveness check against the provider endpoint."""
        pass

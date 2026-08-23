import httpx
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict
from app.core.config import settings
from app.schemas.market import TimeframeEnum
from app.services.market.base import (
    BaseMarketDataProvider,
    ProviderConnectionException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderResponseException,
    AssetNotFoundException,
)
from app.services.market.models import (
    NormalizedAsset,
    NormalizedPrice,
    NormalizedSnapshot,
    NormalizedCandle,
)

logger = logging.getLogger("market.binance")

class BinanceProvider(BaseMarketDataProvider):
    """
    Binance Spot Market REST API provider adapter.
    """
    NAME = "binance"

    TIMEFRAME_MAP = {
        TimeframeEnum.ONE_MINUTE: "1m",
        TimeframeEnum.FIVE_MINUTES: "5m",
        TimeframeEnum.FIFTEEN_MINUTES: "15m",
        TimeframeEnum.THIRTY_MINUTES: "30m",
        TimeframeEnum.ONE_HOUR: "1h",
        TimeframeEnum.FOUR_HOURS: "4h",
        TimeframeEnum.ONE_DAY: "1d",
        TimeframeEnum.ONE_WEEK: "1w",
    }

    def __init__(self):
        self.base_url = getattr(settings, "BINANCE_API_URL", "https://api.binance.com/api/v3").rstrip("/")
        self.api_key = getattr(settings, "BINANCE_API_KEY", "")
        self.timeout = float(getattr(settings, "MARKET_DATA_HTTP_TIMEOUT_SECONDS", 10.0))

    @property
    def name(self) -> str:
        return self.NAME

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key
        return headers

    def _format_symbol(self, symbol: str) -> str:
        s = symbol.upper().strip()
        if not s.endswith("USDT") and not s.endswith("USD"):
            return f"{s}USDT"
        return s

    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Any_Dict:
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self._get_headers())

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    delay = int(retry_after) if retry_after and retry_after.isdigit() else 60
                    raise ProviderRateLimitException(
                        "Binance IP ban/rate limit triggered.",
                        provider=self.NAME,
                        retry_after_seconds=delay,
                    )

                if response.status_code in [400, 404]:
                    data = response.json()
                    if isinstance(data, dict) and data.get("code") in [-1121, -1100]:  # Invalid symbol
                        raise AssetNotFoundException(endpoint, provider=self.NAME)

                if response.status_code >= 500:
                    raise ProviderResponseException(
                        f"Binance server error HTTP {response.status_code}",
                        provider=self.NAME,
                        status_code=response.status_code,
                    )

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as e:
            raise ProviderTimeoutException(f"Binance request timed out: {str(e)}", provider=self.NAME)
        except httpx.NetworkError as e:
            raise ProviderConnectionException(f"Binance network error: {str(e)}", provider=self.NAME)

    async def get_asset(self, symbol_or_id: str) -> Optional[NormalizedAsset]:
        clean_sym = symbol_or_id.upper().replace("USDT", "").replace("USD", "")
        return NormalizedAsset(
            symbol=clean_sym,
            name=f"{clean_sym} Crypto Asset",
            slug=clean_sym.lower(),
            provider_id=self._format_symbol(clean_sym),
            asset_type="crypto",
            status="active",
        )

    async def get_current_price(self, symbol: str) -> NormalizedPrice:
        pair = self._format_symbol(symbol)
        data = await self._request("/ticker/24hr", params={"symbol": pair})
        now = datetime.now(timezone.utc)

        clean_sym = symbol.upper().replace("USDT", "").replace("USD", "")
        price_val = float(data.get("lastPrice", 0.0))

        return NormalizedPrice(
            symbol=clean_sym,
            price=price_val,
            price_change_24h=float(data.get("priceChange", 0.0)),
            price_change_percentage_24h=float(data.get("priceChangePercent", 0.0)),
            high_24h=float(data.get("highPrice", 0.0)),
            low_24h=float(data.get("lowPrice", 0.0)),
            volume_24h=float(data.get("quoteVolume", 0.0)),
            source_timestamp=datetime.fromtimestamp(data.get("closeTime", now.timestamp() * 1000) / 1000, tz=timezone.utc),
            provider=self.NAME,
        )

    async def get_market_snapshot(self, symbol: str) -> NormalizedSnapshot:
        pair = self._format_symbol(symbol)
        data = await self._request("/ticker/24hr", params={"symbol": pair})
        now = datetime.now(timezone.utc)
        clean_sym = symbol.upper().replace("USDT", "").replace("USD", "")

        return NormalizedSnapshot(
            symbol=clean_sym,
            name=f"{clean_sym} Crypto Asset",
            price=float(data.get("lastPrice", 0.0)),
            volume_24h=float(data.get("quoteVolume", 0.0)),
            price_change_24h=float(data.get("priceChange", 0.0)),
            price_change_percentage_24h=float(data.get("priceChangePercent", 0.0)),
            high_24h=float(data.get("highPrice", 0.0)),
            low_24h=float(data.get("lowPrice", 0.0)),
            source_timestamp=datetime.fromtimestamp(data.get("closeTime", now.timestamp() * 1000) / 1000, tz=timezone.utc),
            provider=self.NAME,
        )

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        limit: int = 100,
    ) -> List[NormalizedCandle]:
        pair = self._format_symbol(symbol)
        interval = self.TIMEFRAME_MAP.get(timeframe, "1h")
        raw_klines = await self._request("/klines", params={"symbol": pair, "interval": interval, "limit": min(limit, 1000)})

        candles: List[NormalizedCandle] = []
        if isinstance(raw_klines, list):
            for k in raw_klines:
                # [0: open_time, 1: open, 2: high, 3: low, 4: close, 5: volume, 6: close_time, ...]
                ts = datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc)
                candles.append(
                    NormalizedCandle(
                        timestamp=ts,
                        open=float(k[1]),
                        high=float(k[2]),
                        low=float(k[3]),
                        close=float(k[4]),
                        volume=float(k[5]),
                        timeframe=timeframe,
                        provider=self.NAME,
                    )
                )
        return candles

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        start_time: datetime,
        end_time: datetime,
    ) -> List[NormalizedCandle]:
        pair = self._format_symbol(symbol)
        interval = self.TIMEFRAME_MAP.get(timeframe, "1h")
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)

        raw_klines = await self._request(
            "/klines",
            params={"symbol": pair, "interval": interval, "startTime": start_ms, "endTime": end_ms, "limit": 1000},
        )

        candles: List[NormalizedCandle] = []
        if isinstance(raw_klines, list):
            for k in raw_klines:
                ts = datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc)
                candles.append(
                    NormalizedCandle(
                        timestamp=ts,
                        open=float(k[1]),
                        high=float(k[2]),
                        low=float(k[3]),
                        close=float(k[4]),
                        volume=float(k[5]),
                        timeframe=timeframe,
                        provider=self.NAME,
                    )
                )
        return candles

    async def get_supported_assets(self) -> List[NormalizedAsset]:
        info = await self._request("/exchangeInfo")
        assets: List[NormalizedAsset] = []
        symbols = info.get("symbols", []) if isinstance(info, dict) else []
        for s in symbols[:50]:
            if s.get("quoteAsset") == "USDT" and s.get("status") == "TRADING":
                base = s.get("baseAsset", "")
                assets.append(
                    NormalizedAsset(
                        symbol=base,
                        name=f"{base} Token",
                        slug=base.lower(),
                        provider_id=s.get("symbol", ""),
                        asset_type="crypto",
                        status="active",
                    )
                )
        return assets

    async def health_check(self) -> bool:
        try:
            res = await self._request("/ping")
            return res == {}
        except Exception:
            return False

Any_Dict = Dict[str, Any] | List[Any]

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

logger = logging.getLogger("market.coingecko")

class CoinGeckoProvider(BaseMarketDataProvider):
    """
    CoinGecko REST API market data provider adapter.
    """
    NAME = "coingecko"

    SYMBOL_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "ADA": "cardano",
        "AVAX": "avalanche-2",
        "DOT": "polkadot",
        "LINK": "chainlink",
        "MATIC": "matic-network",
    }

    def __init__(self):
        self.base_url = getattr(settings, "COINGECKO_API_URL", "https://api.coingecko.com/api/v3").rstrip("/")
        self.api_key = getattr(settings, "COINGECKO_API_KEY", "")
        self.timeout = float(getattr(settings, "MARKET_DATA_HTTP_TIMEOUT_SECONDS", 10.0))

    @property
    def name(self) -> str:
        return self.NAME

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key
        return headers

    def _resolve_id(self, symbol_or_id: str) -> str:
        upper = symbol_or_id.upper().strip()
        if upper in self.SYMBOL_MAP:
            return self.SYMBOL_MAP[upper]
        return symbol_or_id.lower().strip()

    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self._get_headers())
                
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    delay = int(retry_after) if retry_after and retry_after.isdigit() else 60
                    raise ProviderRateLimitException(
                        "CoinGecko rate limit exceeded.",
                        provider=self.NAME,
                        retry_after_seconds=delay,
                    )

                if response.status_code == 404:
                    raise AssetNotFoundException(endpoint, provider=self.NAME)

                if response.status_code >= 500:
                    raise ProviderResponseException(
                        f"CoinGecko server error HTTP {response.status_code}",
                        provider=self.NAME,
                        status_code=response.status_code,
                    )

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as e:
            raise ProviderTimeoutException(f"CoinGecko request timed out: {str(e)}", provider=self.NAME)
        except httpx.NetworkError as e:
            raise ProviderConnectionException(f"CoinGecko network error: {str(e)}", provider=self.NAME)

    async def get_asset(self, symbol_or_id: str) -> Optional[NormalizedAsset]:
        coin_id = self._resolve_id(symbol_or_id)
        try:
            data = await self._request(f"/coins/{coin_id}", params={"localization": "false", "tickers": "false", "community_data": "false"})
            return NormalizedAsset(
                symbol=data.get("symbol", "").upper(),
                name=data.get("name", ""),
                slug=data.get("id", ""),
                provider_id=data.get("id", ""),
                asset_type="crypto",
                status="active",
                rank=data.get("market_cap_rank"),
                metadata={"description": data.get("description", {}).get("en", "")[:200]},
            )
        except AssetNotFoundException:
            return None

    async def get_current_price(self, symbol: str) -> NormalizedPrice:
        coin_id = self._resolve_id(symbol)
        data = await self._request(
            "/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true",
            },
        )
        if coin_id not in data:
            raise AssetNotFoundException(symbol, provider=self.NAME)

        entry = data[coin_id]
        ts = datetime.fromtimestamp(entry.get("last_updated_at", datetime.now().timestamp()), tz=timezone.utc)
        price_val = float(entry.get("usd", 0.0))
        pct_change = float(entry.get("usd_24h_change", 0.0)) if entry.get("usd_24h_change") is not None else None

        return NormalizedPrice(
            symbol=symbol.upper(),
            price=price_val,
            price_change_percentage_24h=pct_change,
            volume_24h=float(entry.get("usd_24h_vol", 0.0)) if entry.get("usd_24h_vol") is not None else None,
            source_timestamp=ts,
            provider=self.NAME,
        )

    async def get_market_snapshot(self, symbol: str) -> NormalizedSnapshot:
        coin_id = self._resolve_id(symbol)
        data = await self._request(
            f"/coins/{coin_id}",
            params={"localization": "false", "tickers": "false", "community_data": "false"},
        )
        market_data = data.get("market_data", {})
        current_price = market_data.get("current_price", {}).get("usd", 0.0)
        now = datetime.now(timezone.utc)

        return NormalizedSnapshot(
            symbol=data.get("symbol", symbol).upper(),
            name=data.get("name", ""),
            price=float(current_price),
            market_cap=float(market_data.get("market_cap", {}).get("usd", 0.0)),
            volume_24h=float(market_data.get("total_volume", {}).get("usd", 0.0)),
            price_change_24h=float(market_data.get("price_change_24h", 0.0)) if market_data.get("price_change_24h") is not None else None,
            price_change_percentage_24h=float(market_data.get("price_change_percentage_24h", 0.0)) if market_data.get("price_change_percentage_24h") is not None else None,
            high_24h=float(market_data.get("high_24h", {}).get("usd", 0.0)) if market_data.get("high_24h", {}).get("usd") is not None else None,
            low_24h=float(market_data.get("low_24h", {}).get("usd", 0.0)) if market_data.get("low_24h", {}).get("usd") is not None else None,
            circulating_supply=float(market_data.get("circulating_supply", 0.0)) if market_data.get("circulating_supply") is not None else None,
            total_supply=float(market_data.get("total_supply", 0.0)) if market_data.get("total_supply") is not None else None,
            source_timestamp=now,
            provider=self.NAME,
        )

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        limit: int = 100,
    ) -> List[NormalizedCandle]:
        coin_id = self._resolve_id(symbol)
        # CoinGecko /coins/{id}/ohlc accepts days=1, 7, 14, 30, 90, 180, 365
        days = "1" if timeframe in [TimeframeEnum.ONE_MINUTE, TimeframeEnum.FIVE_MINUTES, TimeframeEnum.FIFTEEN_MINUTES, TimeframeEnum.THIRTY_MINUTES, TimeframeEnum.ONE_HOUR] else "7"
        raw_candles = await self._request(f"/coins/{coin_id}/ohlc", params={"vs_currency": "usd", "days": days})

        candles: List[NormalizedCandle] = []
        if isinstance(raw_candles, list):
            for item in raw_candles[-limit:]:
                if len(item) >= 5:
                    ts = datetime.fromtimestamp(item[0] / 1000, tz=timezone.utc)
                    candles.append(
                        NormalizedCandle(
                            timestamp=ts,
                            open=float(item[1]),
                            high=float(item[2]),
                            low=float(item[3]),
                            close=float(item[4]),
                            volume=0.0,  # CoinGecko OHLC does not return volume in standard tier
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
        # Fallback to get_ohlcv for range
        candles = await self.get_ohlcv(symbol, timeframe, limit=500)
        return [c for c in candles if start_time <= c.timestamp <= end_time]

    async def get_supported_assets(self) -> List[NormalizedAsset]:
        raw_list = await self._request("/coins/list")
        assets: List[NormalizedAsset] = []
        if isinstance(raw_list, list):
            for item in raw_list[:50]:
                assets.append(
                    NormalizedAsset(
                        symbol=item.get("symbol", "").upper(),
                        name=item.get("name", ""),
                        slug=item.get("id", ""),
                        provider_id=item.get("id", ""),
                        asset_type="crypto",
                        status="active",
                    )
                )
        return assets

    async def health_check(self) -> bool:
        try:
            res = await self._request("/ping")
            return "gecko_says" in res
        except Exception:
            return False

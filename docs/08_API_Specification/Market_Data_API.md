# AI TradeQ — Market Data API Specification

**Document Version:** 1.0  
**Status:** Approved  
**Module:** Market Data Intelligence API (Task #003)  
**Classification:** API Specification  

---

## Base Path
All market data endpoints are prefixed with `/api/v1/market`.

---

## Endpoints

### 1. List Cryptocurrency Assets
- **Endpoint**: `GET /api/v1/market/assets`
- **Query Parameters**:
  - `skip` (int, default=0)
  - `limit` (int, default=50, max=250)
  - `status` (string, default="active")
  - `search` (string, optional: filter by symbol or name)
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "symbol": "BTC",
      "name": "Bitcoin",
      "slug": "bitcoin",
      "provider_id": "bitcoin",
      "asset_type": "crypto",
      "status": "active",
      "is_active": true,
      "rank": 1,
      "metadata": { "circulating_supply": 19700000.0 },
      "created_at": "2026-08-23T22:00:00Z",
      "updated_at": "2026-08-23T22:00:00Z"
    }
  ]
  ```

---

### 2. Get Single Asset Metadata
- **Endpoint**: `GET /api/v1/market/assets/{asset_id}`
- **Path Parameters**:
  - `asset_id`: Asset UUID or Symbol (`BTC`, `ETH`)
- **Response**: `200 OK` (Returns `AssetResponse`)

---

### 3. Get Real-Time Price
- **Endpoint**: `GET /api/v1/market/assets/{asset_id}/price`
- **Response**: `200 OK`
  ```json
  {
    "symbol": "BTC",
    "asset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "price": 65420.50,
    "price_change_24h": 1250.30,
    "price_change_percentage_24h": 1.95,
    "high_24h": 66200.00,
    "low_24h": 64100.00,
    "volume_24h": 28400000000.00,
    "freshness": {
      "source_timestamp": "2026-08-23T22:30:00Z",
      "ingested_at": "2026-08-23T22:30:02Z",
      "cached_at": "2026-08-23T22:30:02Z",
      "age_seconds": 2.14,
      "is_stale": false,
      "provider": "binance"
    }
  }
  ```

---

### 4. Get 24-Hour Market Snapshot
- **Endpoint**: `GET /api/v1/market/assets/{asset_id}/snapshot`
- **Response**: `200 OK`
  ```json
  {
    "id": "e9b5f3d4-1a2b-4c3d-8e7f-9a0b1c2d3e4f",
    "asset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": 65420.50,
    "market_cap": 1288800000000.00,
    "volume_24h": 28400000000.00,
    "price_change_24h": 1250.30,
    "price_change_percentage_24h": 1.95,
    "high_24h": 66200.00,
    "low_24h": 64100.00,
    "circulating_supply": 19700000.0,
    "total_supply": 21000000.0,
    "data_timestamp": "2026-08-23T22:30:00Z",
    "freshness": {
      "source_timestamp": "2026-08-23T22:30:00Z",
      "ingested_at": "2026-08-23T22:30:02Z",
      "cached_at": null,
      "age_seconds": 2.14,
      "is_stale": false,
      "provider": "binance"
    }
  }
  ```

---

### 5. Get Latest OHLCV Candlesticks
- **Endpoint**: `GET /api/v1/market/assets/{asset_id}/ohlcv`
- **Query Parameters**:
  - `timeframe`: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w` (default=`1h`)
  - `limit`: int (default=100, max=1000)
- **Response**: `200 OK`
  ```json
  {
    "symbol": "BTC",
    "asset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "timeframe": "1h",
    "count": 100,
    "candles": [
      {
        "timestamp": "2026-08-23T21:00:00Z",
        "open": 65100.00,
        "high": 65550.00,
        "low": 64950.00,
        "close": 65420.50,
        "volume": 1250.45
      }
    ],
    "freshness": {
      "source_timestamp": "2026-08-23T22:00:00Z",
      "ingested_at": "2026-08-23T22:00:02Z",
      "cached_at": "2026-08-23T22:00:02Z",
      "age_seconds": 12.0,
      "is_stale": false,
      "provider": "binance"
    }
  }
  ```

---

### 6. Get Historical Candlesticks
- **Endpoint**: `GET /api/v1/market/assets/{asset_id}/historical`
- **Query Parameters**:
  - `timeframe`: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w` (default=`1d`)
  - `start_time`: ISO 8601 string (e.g. `2026-07-01T00:00:00Z`)
  - `end_time`: ISO 8601 string (e.g. `2026-08-01T00:00:00Z`)
  - `limit`: int (default=250, max=1000)
- **Response**: `200 OK` (Returns `OHLCVResponse` strictly ordered chronologically)

from typing import List
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    PROJECT_NAME: str = "AI TradeQ Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"

    # Security & Authentication Configuration
    SECRET_KEY: str = "SECRET_KEY_PLACEHOLDER_CHANGE_IN_PRODUCTION_32BYTES_MIN"
    JWT_SECRET: str = "SECRET_KEY_PLACEHOLDER_CHANGE_IN_PRODUCTION_32BYTES_MIN"
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Account Lockout & Brute Force Protection
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # Password Policy Configuration
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # Rate Limiting Configuration
    RATE_LIMIT_PER_MINUTE_AUTH: int = 10
    DEFAULT_USER_ROLE: str = "USER"

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgrespassword"
    POSTGRES_DB: str = "aitradeq_db"
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:postgrespassword@localhost:5432/aitradeq_db"

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Market Data Provider Configuration
    PRIMARY_MARKET_DATA_PROVIDER: str = "mock"
    FALLBACK_MARKET_DATA_PROVIDER: str = "mock"
    COINGECKO_API_KEY: str = ""
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    BINANCE_API_URL: str = "https://api.binance.com/api/v3"

    # Market Data Caching & TTLs (Seconds)
    MARKET_CACHE_PRICE_TTL_SECONDS: int = 15
    MARKET_CACHE_SNAPSHOT_TTL_SECONDS: int = 60
    MARKET_CACHE_OHLCV_TTL_SECONDS: int = 60
    MARKET_CACHE_ASSETS_TTL_SECONDS: int = 3600

    # Market Data Freshness Thresholds (Seconds)
    MARKET_DATA_MAX_STALENESS_PRICE_SECONDS: int = 60
    MARKET_DATA_MAX_STALENESS_SNAPSHOT_SECONDS: int = 300
    MARKET_DATA_HTTP_TIMEOUT_SECONDS: float = 10.0
    MARKET_DATA_MAX_RETRIES: int = 3

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

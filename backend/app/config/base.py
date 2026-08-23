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

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

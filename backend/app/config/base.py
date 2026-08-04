from typing import List
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    PROJECT_NAME: str = "AI TradeQ Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"

    SECRET_KEY: str = "SECRET_KEY_PLACEHOLDER_CHANGE_IN_PRODUCTION_32BYTES_MIN"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgrespassword"
    POSTGRES_DB: str = "aitradeq_db"
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:postgrespassword@localhost:5432/aitradeq_db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        case_sensitive = True
        env_file = ".env"

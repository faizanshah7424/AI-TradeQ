from app.config.base import BaseConfig

class TestingConfig(BaseConfig):
    APP_ENV: str = "testing"
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

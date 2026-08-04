from app.config.base import BaseConfig

class ProductionConfig(BaseConfig):
    APP_ENV: str = "production"
    DEBUG: bool = False

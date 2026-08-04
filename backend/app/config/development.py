from app.config.base import BaseConfig

class DevelopmentConfig(BaseConfig):
    APP_ENV: str = "development"
    DEBUG: bool = True

from app.config.base import BaseConfig

class StagingConfig(BaseConfig):
    APP_ENV: str = "staging"
    DEBUG: bool = False

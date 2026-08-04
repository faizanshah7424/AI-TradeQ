import os
from app.config.base import BaseConfig
from app.config.development import DevelopmentConfig
from app.config.testing import TestingConfig
from app.config.staging import StagingConfig
from app.config.production import ProductionConfig

def get_settings() -> BaseConfig:
    env = os.getenv("APP_ENV", "development").lower()
    if env == "testing":
        return TestingConfig()
    elif env == "staging":
        return StagingConfig()
    elif env == "production":
        return ProductionConfig()
    return DevelopmentConfig()

settings = get_settings()

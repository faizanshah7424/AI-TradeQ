from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine_kwargs = {"pool_pre_ping": True}
if "sqlite" in settings.SQLALCHEMY_DATABASE_URI:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

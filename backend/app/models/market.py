import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CryptoAsset(Base):
    __tablename__ = "crypto_assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    provider_id = Column(String(100), nullable=False, index=True)
    asset_type = Column(String(20), nullable=False, default="crypto")
    status = Column(String(20), nullable=False, default="active", index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    rank = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    snapshots = relationship("MarketSnapshot", back_populates="asset", cascade="all, delete-orphan")
    candles = relationship("OHLCVCandle", back_populates="asset", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("symbol", "provider_id", name="uq_asset_symbol_provider"),
    )

    def __repr__(self) -> str:
        return f"<CryptoAsset symbol={self.symbol} name={self.name}>"


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    asset_id = Column(String(36), ForeignKey("crypto_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    price_change_percentage_24h = Column(Float, nullable=True)
    high_24h = Column(Float, nullable=True)
    low_24h = Column(Float, nullable=True)
    circulating_supply = Column(Float, nullable=True)
    total_supply = Column(Float, nullable=True)
    provider = Column(String(50), nullable=False, default="unknown")
    data_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    asset = relationship("CryptoAsset", back_populates="snapshots")

    __table_args__ = (
        Index("ix_snapshot_asset_timestamp", "asset_id", "data_timestamp"),
    )

    def __repr__(self) -> str:
        return f"<MarketSnapshot asset_id={self.asset_id} price={self.price} ts={self.data_timestamp}>"


class OHLCVCandle(Base):
    __tablename__ = "ohlcv_candles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    asset_id = Column(String(36), ForeignKey("crypto_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    candle_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    provider = Column(String(50), nullable=False, default="unknown")
    ingested_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    asset = relationship("CryptoAsset", back_populates="candles")

    __table_args__ = (
        UniqueConstraint("asset_id", "timeframe", "candle_timestamp", "provider", name="uq_candle_asset_tf_ts_prov"),
        Index("ix_ohlcv_asset_tf_ts", "asset_id", "timeframe", "candle_timestamp"),
    )

    def __repr__(self) -> str:
        return f"<OHLCVCandle asset_id={self.asset_id} tf={self.timeframe} c={self.close} ts={self.candle_timestamp}>"

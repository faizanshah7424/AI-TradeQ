import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    family_id = Column(String(36), index=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken user_id={self.user_id} revoked={self.is_revoked}>"

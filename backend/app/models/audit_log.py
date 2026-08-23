import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AuthAuditLog(Base):
    __tablename__ = "auth_audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # SUCCESS, FAILURE
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    correlation_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuthAuditLog event={self.event_type} status={self.status}>"

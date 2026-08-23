import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles", lazy="joined")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

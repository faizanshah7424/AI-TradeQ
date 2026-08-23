import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
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
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # RBAC & Token Relationships
    roles = relationship("Role", secondary="user_roles", back_populates="users", lazy="joined")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuthAuditLog", back_populates="user", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or ""

    @property
    def role_names(self) -> list[str]:
        return [role.name for role in self.roles]

    @property
    def permission_names(self) -> list[str]:
        perms = set()
        for role in self.roles:
            for perm in role.permissions:
                perms.add(perm.name)
        return list(perms)

    def is_currently_locked(self) -> bool:
        if not self.is_locked:
            return False
        if self.locked_until is None:
            return True
        return datetime.now(timezone.utc) < self.locked_until

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

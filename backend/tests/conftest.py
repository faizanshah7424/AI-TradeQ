import os
import uuid
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set testing environment before importing app
os.environ["APP_ENV"] = "testing"

from app.db.base_class import Base
from app.api.deps import get_db
from app.main import app
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.core.security import get_password_hash, create_access_token

# In-memory SQLite engine for tests with static connection pool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session() -> Generator:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Seed default roles if not present
    for role_name, desc in [
        ("SUPER_ADMIN", "Super Administrator"),
        ("ADMIN", "System Administrator"),
        ("ANALYST", "Market Analyst"),
        ("USER", "Standard User"),
    ]:
        if not session.query(Role).filter(Role.name == role_name).first():
            session.add(Role(name=role_name, description=desc))
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session) -> Generator:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session) -> User:
    user_role = db_session.query(Role).filter(Role.name == "USER").first()
    user = User(
        email="test.user@example.com",
        password_hash=get_password_hash("SecurePassword123!"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
        is_locked=False,
    )
    if user_role:
        user.roles.append(user_role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session) -> User:
    admin_role = db_session.query(Role).filter(Role.name == "ADMIN").first()
    user = User(
        email="admin.user@example.com",
        password_hash=get_password_hash("AdminSecurePassword123!"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_verified=True,
        is_locked=False,
    )
    if admin_role:
        user.roles.append(admin_role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def user_auth_headers(test_user) -> dict:
    token = create_access_token(
        subject=test_user.id,
        roles=test_user.role_names,
        permissions=test_user.permission_names,
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(admin_user) -> dict:
    token = create_access_token(
        subject=admin_user.id,
        roles=admin_user.role_names,
        permissions=admin_user.permission_names,
    )
    return {"Authorization": f"Bearer {token}"}

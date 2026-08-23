import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status
from app.models.user import User

def test_successful_login(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "SecurePassword123!",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0

def test_invalid_password_login(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid email or password" in response.json().get("message", "").lower()

def test_unknown_email_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent.user@example.com",
            "password": "SomePassword123!",
        },
    )
    # Generic failure response without leaking existence
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid email or password" in response.json().get("message", "").lower()

def test_account_lockout_after_consecutive_failed_attempts(client, test_user, db_session):
    # Perform 5 failed login attempts
    for _ in range(5):
        client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "IncorrectPassword!",
            },
        )

    # 6th attempt should return 403 Forbidden due to lockout
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "SecurePassword123!",
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "locked" in response.json().get("message", "").lower()

def test_deactivated_account_login(client, test_user, db_session):
    test_user.is_active = False
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "SecurePassword123!",
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "deactivated" in response.json().get("message", "").lower()

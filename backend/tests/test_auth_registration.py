import pytest
from fastapi import status

def test_successful_registration(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new.user@example.com",
            "password": "Password123!",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    # Ensure sensitive hashes are not exposed
    assert "password" not in data
    assert "password_hash" not in data

def test_duplicate_email_registration(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "AnotherPassword123!",
            "first_name": "Duplicate",
            "last_name": "User",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json().get("message", "").lower()

def test_invalid_email_registration(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-a-valid-email",
            "password": "Password123!",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_weak_password_registration(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak.password@example.com",
            "password": "short",
        },
    )
    # Fails Pydantic validation or policy
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

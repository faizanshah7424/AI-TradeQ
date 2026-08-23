import pytest
from datetime import timedelta
from fastapi import status
from app.core.security import create_access_token
from app.models.refresh_token import RefreshToken

def test_valid_access_token_me_endpoint(client, user_auth_headers, test_user):
    response = client.get("/api/v1/auth/me", headers=user_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert "password" not in data
    assert "password_hash" not in data

def test_expired_access_token(client, test_user):
    expired_token = create_access_token(
        subject=test_user.id,
        expires_delta=timedelta(seconds=-10),
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_invalid_signature_access_token(client):
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalidsignature"
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_refresh_token_rotation(client, test_user):
    # 1. Login to obtain token pair
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )
    tokens = login_res.json()
    initial_refresh = tokens["refresh_token"]

    # 2. Refresh token
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    assert refresh_res.status_code == status.HTTP_200_OK
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["refresh_token"] != initial_refresh

    # 3. Presenting the old (already rotated/revoked) refresh token must trigger reuse detection
    reuse_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    assert reuse_res.status_code == status.HTTP_401_UNAUTHORIZED
    assert "reuse detected" in reuse_res.json().get("message", "").lower()

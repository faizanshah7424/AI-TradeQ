import pytest
from fastapi import status

def test_single_session_logout(client, test_user):
    # Login to get token pair
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Logout single session
    logout_res = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == status.HTTP_200_OK

    # Refreshing with the logged-out refresh token must fail
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == status.HTTP_401_UNAUTHORIZED

def test_logout_all_sessions(client, test_user, user_auth_headers):
    # Obtain 2 refresh tokens
    login1 = client.post("/api/v1/auth/login", json={"email": test_user.email, "password": "SecurePassword123!"})
    rf1 = login1.json()["refresh_token"]

    login2 = client.post("/api/v1/auth/login", json={"email": test_user.email, "password": "SecurePassword123!"})
    rf2 = login2.json()["refresh_token"]

    # Call logout-all
    logout_all_res = client.post("/api/v1/auth/logout-all", headers=user_auth_headers)
    assert logout_all_res.status_code == status.HTTP_200_OK
    assert "successfully logged out" in logout_all_res.json()["message"].lower()

    # Both refresh tokens must be revoked
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": rf1}).status_code == status.HTTP_401_UNAUTHORIZED
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": rf2}).status_code == status.HTTP_401_UNAUTHORIZED

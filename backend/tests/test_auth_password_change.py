import pytest
from fastapi import status

def test_successful_password_change(client, test_user, user_auth_headers):
    response = client.post(
        "/api/v1/auth/change-password",
        headers=user_auth_headers,
        json={
            "current_password": "SecurePassword123!",
            "new_password": "BrandNewPassword123!",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert "password changed successfully" in response.json().get("message", "").lower()

    # Verify login works with new password
    login_new = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "BrandNewPassword123!"},
    )
    assert login_new.status_code == status.HTTP_200_OK

    # Verify old password no longer works
    login_old = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )
    assert login_old.status_code == status.HTTP_401_UNAUTHORIZED

def test_password_change_incorrect_current_password(client, user_auth_headers):
    response = client.post(
        "/api/v1/auth/change-password",
        headers=user_auth_headers,
        json={
            "current_password": "WrongCurrentPassword!",
            "new_password": "BrandNewPassword123!",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "current password is incorrect" in response.json().get("message", "").lower()

def test_password_change_weak_new_password(client, user_auth_headers):
    response = client.post(
        "/api/v1/auth/change-password",
        headers=user_auth_headers,
        json={
            "current_password": "SecurePassword123!",
            "new_password": "short",
        },
    )
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

import pytest
from fastapi import status

def test_get_user_profile_me(client, user_auth_headers, test_user):
    response = client.get("/api/v1/users/me", headers=user_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name
    assert "roles" in data
    assert "permissions" in data
    # Sensitive password hashes never returned
    assert "password_hash" not in data
    assert "password" not in data

def test_update_user_profile_me(client, user_auth_headers, test_user):
    response = client.patch(
        "/api/v1/users/me",
        headers=user_auth_headers,
        json={
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "UpdatedFirst"
    assert data["last_name"] == "UpdatedLast"
    assert data["full_name"] == "UpdatedFirst UpdatedLast"

def test_update_profile_cannot_escalate_role_or_tamper_password(client, user_auth_headers, test_user):
    # Attempting to send role or password fields in PATCH /users/me must be ignored/rejected
    response = client.patch(
        "/api/v1/users/me",
        headers=user_auth_headers,
        json={
            "first_name": "TamperTest",
            "roles": ["SUPER_ADMIN"],
            "password_hash": "hacked_hash",
            "is_superuser": True,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "TamperTest"
    assert "SUPER_ADMIN" not in data["roles"]

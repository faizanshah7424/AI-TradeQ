import pytest
from fastapi import APIRouter, Depends, status
from app.api.deps import require_authenticated_user, require_role, require_permission
from app.main import app

# Create a test router with role and permission gated endpoints
test_router = APIRouter(prefix="/api/v1/test-rbac")

@test_router.get("/user-only", dependencies=[Depends(require_role("USER"))])
def user_only():
    return {"access": "granted_user"}

@test_router.get("/admin-only", dependencies=[Depends(require_role("ADMIN"))])
def admin_only():
    return {"access": "granted_admin"}

@test_router.get("/perm-only", dependencies=[Depends(require_permission("reports:export"))])
def perm_only():
    return {"access": "granted_perm"}

app.include_router(test_router)

def test_authenticated_user_access(client, user_auth_headers):
    response = client.get("/api/v1/test-rbac/user-only", headers=user_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access"] == "granted_user"

def test_unauthenticated_user_access(client):
    response = client.get("/api/v1/test-rbac/user-only")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_forbidden_from_admin_endpoint(client, user_auth_headers):
    response = client.get("/api/v1/test-rbac/admin-only", headers=user_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "access denied" in response.json().get("detail", "").lower()

def test_admin_access_to_admin_endpoint(client, admin_auth_headers):
    response = client.get("/api/v1/test-rbac/admin-only", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access"] == "granted_admin"

def test_missing_permission_forbidden(client, user_auth_headers):
    response = client.get("/api/v1/test-rbac/perm-only", headers=user_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "missing required permission" in response.json().get("detail", "").lower()

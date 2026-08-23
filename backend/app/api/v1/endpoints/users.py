from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_authenticated_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import user_service

router = APIRouter()

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
def get_user_profile(
    current_user: User = Depends(require_authenticated_user),
):
    """
    Retrieve profile information for the authenticated user.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_locked=current_user.is_locked,
        roles=current_user.role_names,
        permissions=current_user.permission_names,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login_at=current_user.last_login_at,
    )

@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
)
def update_user_profile(
    payload: UserUpdate,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Update safe user profile fields (first name, last name).
    Explicitly prohibits modifications to sensitive fields such as role, permissions, status, or password.
    """
    updated_user = user_service.update_profile(db=db, user=current_user, update_data=payload)
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        full_name=updated_user.full_name,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        is_locked=updated_user.is_locked,
        roles=updated_user.role_names,
        permissions=updated_user.permission_names,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        last_login_at=updated_user.last_login_at,
    )

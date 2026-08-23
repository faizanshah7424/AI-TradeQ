from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_authenticated_user
from app.core.rate_limit import rate_limit_dependency, get_client_ip
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    TokenResponse,
    MessageResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service

router = APIRouter()

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    dependencies=[Depends(rate_limit_dependency(max_requests=10, window_seconds=60))],
)
def register(
    request: Request,
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user, validate password complexity, assign the default role,
    and return an initial access and refresh token pair.
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    correlation_id = request.headers.get("X-Correlation-ID")

    _, token_response = auth_service.register_user(
        db=db,
        request=payload,
        ip_address=client_ip,
        user_agent=user_agent,
        correlation_id=correlation_id,
    )
    return token_response

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain token pair",
    dependencies=[Depends(rate_limit_dependency(max_requests=10, window_seconds=60))],
)
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate email and password, check lockout rules, track attempts,
    and return a new access and refresh token pair.
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    correlation_id = request.headers.get("X-Correlation-ID")

    _, token_response = auth_service.login_user(
        db=db,
        request=payload,
        ip_address=client_ip,
        user_agent=user_agent,
        correlation_id=correlation_id,
    )
    return token_response

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token and issue new access token",
    dependencies=[Depends(rate_limit_dependency(max_requests=20, window_seconds=60))],
)
def refresh(
    request: Request,
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Present a valid unrevoked refresh token to obtain a rotated refresh token
    and a fresh short-lived access token. Implements automatic token reuse detection.
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    correlation_id = request.headers.get("X-Correlation-ID")

    return auth_service.refresh_access_token(
        db=db,
        refresh_token_str=payload.refresh_token,
        ip_address=client_ip,
        user_agent=user_agent,
        correlation_id=correlation_id,
    )

@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke current session refresh token",
)
def logout(
    request: Request,
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Revoke a single refresh token session.
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    correlation_id = request.headers.get("X-Correlation-ID")

    auth_service.logout_session(
        db=db,
        refresh_token_str=payload.refresh_token,
        ip_address=client_ip,
        user_agent=user_agent,
        correlation_id=correlation_id,
    )
    return MessageResponse(message="Successfully logged out session.")

@router.post(
    "/logout-all",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke all active sessions for authenticated user",
)
def logout_all(
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Revoke all active refresh tokens and sessions for the authenticated user.
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    correlation_id = request.headers.get("X-Correlation-ID")

    count = auth_service.logout_all_sessions(
        db=db,
        user_id=current_user.id,
        ip_address=client_ip,
        user_agent=user_agent,
        correlation_id=correlation_id,
    )
    return MessageResponse(message=f"Successfully logged out {count} active session(s).")

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user identity details",
)
def get_me(
    current_user: User = Depends(require_authenticated_user),
):
    """
    Retrieve authenticated user profile, roles, and effective permissions.
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

@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password for authenticated user",
    dependencies=[Depends(rate_limit_dependency(max_requests=5, window_seconds=60))],
)
def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Verify current password, validate new password requirements, update hash,
    and invalidate all existing active sessions.
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    correlation_id = request.headers.get("X-Correlation-ID")

    auth_service.change_password(
        db=db,
        user=current_user,
        request=payload,
        ip_address=client_ip,
        user_agent=user_agent,
        correlation_id=correlation_id,
    )
    return MessageResponse(message="Password changed successfully. All active sessions have been invalidated.")

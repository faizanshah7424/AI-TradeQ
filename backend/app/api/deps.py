from typing import Generator, Optional, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User
from app.services.audit_service import audit_service

# Bearer token extractor
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)

http_bearer_scheme = HTTPBearer(auto_error=False)

def get_db() -> Generator[Session, None, None]:
    """Provide transactional database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer_scheme),
    token_str: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """
    Extract and validate JWT access token from Authorization header or OAuth2 bearer.
    Resolves authenticated User from database.
    """
    token = None
    if auth_header and auth_header.credentials:
        token = auth_header.credentials
    elif token_str:
        token = token_str

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims: subject missing.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify that current user account is active and not locked."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )
    if current_user.is_currently_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked. Please try again later.",
        )
    return current_user

require_authenticated_user = get_current_active_user

def require_role(*allowed_roles: str) -> Callable[[User], User]:
    """
    Authorization dependency ensuring current user possesses at least one of the specified roles.
    SUPER_ADMIN always satisfies role requirements.
    """
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        user_roles = set(current_user.role_names)
        if "SUPER_ADMIN" in user_roles:
            return current_user

        if not any(role in user_roles for role in allowed_roles):
            audit_service.log_event(
                db=db,
                event_type="ACCESS_DENIED",
                status="FAILURE",
                user_id=current_user.id,
                details={"required_roles": list(allowed_roles), "user_roles": list(user_roles)},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker

def require_permission(*required_permissions: str) -> Callable[[User], User]:
    """
    Authorization dependency ensuring current user possesses all specified permissions.
    SUPER_ADMIN always satisfies permission requirements.
    """
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        user_perms = set(current_user.permission_names)
        user_roles = set(current_user.role_names)

        if "SUPER_ADMIN" in user_roles:
            return current_user

        missing = [p for p in required_permissions if p not in user_perms]
        if missing:
            audit_service.log_event(
                db=db,
                event_type="ACCESS_DENIED",
                status="FAILURE",
                user_id=current_user.id,
                details={"missing_permissions": missing},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Missing required permission(s): {', '.join(missing)}",
            )
        return current_user

    return permission_checker

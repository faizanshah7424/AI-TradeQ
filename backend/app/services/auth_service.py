import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import ServiceException
from app.core.security import (
    verify_password,
    get_password_hash,
    validate_password_policy,
    create_access_token,
    generate_refresh_token,
    hash_token,
)
from app.models.user import User
from app.models.role import Role
from app.models.refresh_token import RefreshToken
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ChangePasswordRequest,
    TokenResponse,
)
from app.services.audit_service import audit_service

class AuthService:
    @staticmethod
    def _create_token_pair(
        db: Session,
        user: User,
        family_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[str, str, int]:
        """Helper to create access token, generate refresh token, and persist hashed refresh token."""
        # 1. Access Token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id,
            roles=user.role_names,
            permissions=user.permission_names,
            expires_delta=access_token_expires,
        )

        # 2. Refresh Token
        raw_refresh_token = generate_refresh_token()
        hashed_rf = hash_token(raw_refresh_token)
        refresh_expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_family = family_id or str(uuid.uuid4())

        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hashed_rf,
            family_id=token_family,
            is_revoked=False,
            expires_at=refresh_expires,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.add(db_refresh_token)

        expires_in_seconds = int(access_token_expires.total_seconds())
        return access_token, raw_refresh_token, expires_in_seconds

    @classmethod
    def register_user(
        cls,
        db: Session,
        request: RegisterRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Tuple[User, TokenResponse]:
        """
        Register a new user, validate password policy, assign default role, and issue token pair.
        """
        normalized_email = request.email.lower().strip()

        # Check existing user
        existing_user = db.query(User).filter(User.email == normalized_email).first()
        if existing_user:
            audit_service.log_event(
                db=db,
                event_type="REGISTER",
                status="FAILURE",
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"email": normalized_email, "reason": "Email already exists"},
            )
            raise ServiceException("An account with this email address already exists.", status_code=409)

        # Validate password policy
        is_valid_pw, pw_error = validate_password_policy(request.password)
        if not is_valid_pw:
            audit_service.log_event(
                db=db,
                event_type="REGISTER",
                status="FAILURE",
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"email": normalized_email, "reason": pw_error},
            )
            raise ServiceException(pw_error or "Password does not meet security requirements.", status_code=400)

        # Hash password and create user
        password_hash = get_password_hash(request.password)
        new_user = User(
            email=normalized_email,
            password_hash=password_hash,
            first_name=request.first_name.strip() if request.first_name else None,
            last_name=request.last_name.strip() if request.last_name else None,
            is_active=True,
            is_verified=False,
            is_locked=False,
        )

        # Assign default role (e.g. USER)
        default_role_name = getattr(settings, "DEFAULT_USER_ROLE", "USER")
        default_role = db.query(Role).filter(Role.name == default_role_name).first()
        if not default_role:
            default_role = Role(name=default_role_name, description="Standard Platform User")
            db.add(default_role)
            db.flush()
        new_user.roles.append(default_role)

        db.add(new_user)
        db.flush()

        # Create session tokens
        access_token, refresh_token, expires_in = cls._create_token_pair(
            db=db, user=new_user, ip_address=ip_address, user_agent=user_agent
        )

        db.commit()
        db.refresh(new_user)

        audit_service.log_event(
            db=db,
            event_type="REGISTER",
            status="SUCCESS",
            user_id=new_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            details={"email": normalized_email, "role": default_role_name},
        )

        return new_user, TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    @classmethod
    def login_user(
        cls,
        db: Session,
        request: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Tuple[User, TokenResponse]:
        """
        Authenticate user credentials, check lockout, handle failed attempts, and issue session tokens.
        """
        normalized_email = request.email.lower().strip()
        user = db.query(User).filter(User.email == normalized_email).first()

        # Generic authentication failure if user does not exist
        if not user:
            audit_service.log_event(
                db=db,
                event_type="LOGIN_FAILURE",
                status="FAILURE",
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"email": normalized_email, "reason": "User not found"},
            )
            raise ServiceException("Invalid email or password.", status_code=401)

        # Check account lockout
        if user.is_currently_locked():
            audit_service.log_event(
                db=db,
                event_type="ACCOUNT_LOCKOUT",
                status="BLOCKED",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"email": normalized_email, "locked_until": str(user.locked_until)},
            )
            raise ServiceException(
                "Account is temporarily locked due to consecutive failed login attempts. Please try again later.",
                status_code=403,
            )

        # Check account active status
        if not user.is_active:
            audit_service.log_event(
                db=db,
                event_type="LOGIN_FAILURE",
                status="FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"email": normalized_email, "reason": "Account deactivated"},
            )
            raise ServiceException("Account is deactivated. Please contact support.", status_code=403)

        # Verify password
        if not verify_password(request.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.is_locked = True
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
                audit_service.log_event(
                    db=db,
                    event_type="ACCOUNT_LOCKOUT",
                    status="LOCKED",
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    correlation_id=correlation_id,
                    details={"failed_attempts": user.failed_login_attempts},
                )
            else:
                audit_service.log_event(
                    db=db,
                    event_type="LOGIN_FAILURE",
                    status="FAILURE",
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    correlation_id=correlation_id,
                    details={"failed_attempts": user.failed_login_attempts},
                )
            db.commit()
            raise ServiceException("Invalid email or password.", status_code=401)

        # Login succeeded: reset failed attempts & lockout
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)

        access_token, refresh_token, expires_in = cls._create_token_pair(
            db=db, user=user, ip_address=ip_address, user_agent=user_agent
        )

        db.commit()
        db.refresh(user)

        audit_service.log_event(
            db=db,
            event_type="LOGIN_SUCCESS",
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            details={"email": normalized_email},
        )

        return user, TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    @classmethod
    def refresh_access_token(
        cls,
        db: Session,
        refresh_token_str: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> TokenResponse:
        """
        Validate refresh token, detect reuse attacks, rotate token within its family, and issue new pair.
        """
        token_hash_val = hash_token(refresh_token_str)
        token_record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash_val).first()

        if not token_record:
            audit_service.log_event(
                db=db,
                event_type="TOKEN_REFRESH",
                status="FAILURE",
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"reason": "Refresh token not found"},
            )
            raise ServiceException("Invalid or expired refresh token.", status_code=401)

        # Token Reuse Detection: If a revoked token is presented, revoke the entire token family
        if token_record.is_revoked:
            # Revoke all tokens in family
            db.query(RefreshToken).filter(RefreshToken.family_id == token_record.family_id).update(
                {"is_revoked": True, "revoked_at": datetime.now(timezone.utc)}
            )
            db.commit()

            audit_service.log_event(
                db=db,
                event_type="TOKEN_REUSE_DETECTED",
                status="SECURITY_ALERT",
                user_id=token_record.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"family_id": token_record.family_id, "action": "Invalidated all sessions in family"},
            )
            raise ServiceException("Security violation: Token reuse detected. All active sessions have been revoked.", status_code=401)

        # Check token expiration
        now = datetime.now(timezone.utc)
        if token_record.expires_at < now:
            token_record.is_revoked = True
            token_record.revoked_at = now
            db.commit()
            audit_service.log_event(
                db=db,
                event_type="TOKEN_REFRESH",
                status="FAILURE",
                user_id=token_record.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"reason": "Refresh token expired"},
            )
            raise ServiceException("Refresh token has expired. Please log in again.", status_code=401)

        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user or not user.is_active or user.is_currently_locked():
            token_record.is_revoked = True
            token_record.revoked_at = now
            db.commit()
            raise ServiceException("User account is inactive, locked, or not found.", status_code=401)

        # Rotate token: revoke current token and create new child token in the same family
        token_record.is_revoked = True
        token_record.revoked_at = now

        access_token, new_refresh_token, expires_in = cls._create_token_pair(
            db=db,
            user=user,
            family_id=token_record.family_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.commit()

        audit_service.log_event(
            db=db,
            event_type="TOKEN_REFRESH",
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            details={"family_id": token_record.family_id},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    @classmethod
    def logout_session(
        cls,
        db: Session,
        refresh_token_str: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> bool:
        """Revoke a single refresh token session."""
        token_hash_val = hash_token(refresh_token_str)
        token_record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash_val).first()

        if token_record and not token_record.is_revoked:
            token_record.is_revoked = True
            token_record.revoked_at = datetime.now(timezone.utc)
            db.commit()

            audit_service.log_event(
                db=db,
                event_type="LOGOUT",
                status="SUCCESS",
                user_id=token_record.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
            )
            return True

        audit_service.log_event(
            db=db,
            event_type="LOGOUT",
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            details={"note": "Token was not found or already revoked"},
        )
        return True

    @classmethod
    def logout_all_sessions(
        cls,
        db: Session,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> int:
        """Revoke all active refresh tokens and sessions for a user."""
        now = datetime.now(timezone.utc)
        count = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        ).update({"is_revoked": True, "revoked_at": now})

        db.commit()

        audit_service.log_event(
            db=db,
            event_type="LOGOUT_ALL",
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            details={"revoked_sessions_count": count},
        )
        return count

    @classmethod
    def change_password(
        cls,
        db: Session,
        user: User,
        request: ChangePasswordRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> bool:
        """Verify current password, validate new password policy, update hash, and invalidate all existing sessions."""
        if not verify_password(request.current_password, user.password_hash):
            audit_service.log_event(
                db=db,
                event_type="PASSWORD_CHANGE",
                status="FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"reason": "Incorrect current password"},
            )
            raise ServiceException("Current password is incorrect.", status_code=400)

        is_valid_pw, pw_error = validate_password_policy(request.new_password)
        if not is_valid_pw:
            audit_service.log_event(
                db=db,
                event_type="PASSWORD_CHANGE",
                status="FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                details={"reason": pw_error},
            )
            raise ServiceException(pw_error or "New password does not meet security requirements.", status_code=400)

        # Update password hash
        user.password_hash = get_password_hash(request.new_password)

        # Invalidate all existing refresh tokens for security
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False,
        ).update({"is_revoked": True, "revoked_at": datetime.now(timezone.utc)})

        db.commit()

        audit_service.log_event(
            db=db,
            event_type="PASSWORD_CHANGE",
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            details={"action": "Password changed and existing sessions invalidated"},
        )
        return True

auth_service = AuthService()

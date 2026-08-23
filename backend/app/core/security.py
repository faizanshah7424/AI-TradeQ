import uuid
import secrets
import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union, Dict, List
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Safely verify a plaintext password against its bcrypt hash in constant time."""
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Generate a secure cryptographic hash for the given password."""
    return pwd_context.hash(password)

def validate_password_policy(password: str) -> tuple[bool, Optional[str]]:
    """
    Enforce enterprise password complexity requirements based on configuration.
    Returns (True, None) if compliant, or (False, error_message) if invalid.
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long."

    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        return False, "Password must contain at least one numeric digit."

    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."

    return True, None

def create_access_token(
    subject: Union[str, Any],
    roles: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT access token with standardized claims."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
        "roles": roles or [],
        "permissions": permissions or [],
    }

    secret = getattr(settings, "JWT_SECRET", settings.SECRET_KEY)
    algorithm = getattr(settings, "JWT_ALGORITHM", settings.ALGORITHM)
    return jwt.encode(to_encode, secret, algorithm=algorithm)

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Raises JWTError if token is expired, corrupted, or signature is invalid.
    """
    secret = getattr(settings, "JWT_SECRET", settings.SECRET_KEY)
    algorithm = getattr(settings, "JWT_ALGORITHM", settings.ALGORITHM)
    payload = jwt.decode(token, secret, algorithms=[algorithm])

    if payload.get("type") != "access":
        raise JWTError("Invalid token type")

    return payload

def generate_refresh_token() -> str:
    """Generate a cryptographically secure random refresh token string."""
    return secrets.token_urlsafe(64)

def hash_token(token: str) -> str:
    """Generate a SHA-256 hash of a refresh token for safe database persistence."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

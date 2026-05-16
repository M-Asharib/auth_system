from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import hashlib
import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash of a password."""
    return pwd_context.hash(password)


def create_token(
    subject: Union[str, Any],
    expires_delta: timedelta,
    token_type: str,  # "access" or "refresh"
    secret_key: str,
    fingerprint: Optional[str] = None
) -> str:
    """
    Create a JWT token with explicit structural attributes.
    v1.4.2 Requirement: identifying exact operational usage.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": token_type,  # Explicit structural attribute
        "iat": datetime.now(timezone.utc)
    }

    if fingerprint:
        # Hash fingerprint to keep it privacy-safe in JWT
        to_encode["fpt"] = hashlib.sha256(fingerprint.encode()).hexdigest()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    fingerprint: Optional[str] = None
) -> str:
    """Generate a short-lived access token with optional custom expiry."""
    if expires_delta:
        expires = expires_delta
    else:
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    return create_token(
        subject=subject,
        expires_delta=expires,
        token_type="access",
        secret_key=settings.SECRET_KEY_ACCESS,  # nosec B106
        fingerprint=fingerprint
    )


def create_refresh_token(
    subject: Union[str, Any],
    fingerprint: Optional[str] = None
) -> str:
    """Generate a long-lived refresh token."""
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(
        subject=subject,
        expires_delta=expires,
        token_type="refresh",
        secret_key=settings.SECRET_KEY_REFRESH,  # nosec B106
        fingerprint=fingerprint
    )

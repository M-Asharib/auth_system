from fastapi import APIRouter, Depends, HTTPException, status, Body, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt
from typing import Any, Optional
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRegistrationResponse
from app.schemas.token import TokenExchangeResponse, TokenPayload
from app.schemas.msg import StandardActionResponse
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.api.deps import get_current_user, reusable_oauth2
from app.services.redis_service import redis_service
from app.core.config import settings
from datetime import datetime, timezone
from pydantic import ValidationError

router = APIRouter()

@router.post("/register", response_model=UserRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )
    
    # Create new user
    db_obj = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_superuser=False
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


@router.post("/login", response_model=TokenExchangeResponse)
async def login(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends(),
    x_device_fingerprint: Optional[str] = Header(None)
):
    # Authenticate user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    # Check for user-wise expiry override
    expires_delta = None
    if user.access_token_expires_minutes:
        from datetime import timedelta
        expires_delta = timedelta(minutes=user.access_token_expires_minutes)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    return {
        "access_token": create_access_token(
            user.id, 
            expires_delta=expires_delta,
            fingerprint=x_device_fingerprint
        ),
        "refresh_token": create_refresh_token(
            user.id,
            fingerprint=x_device_fingerprint
        ),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenExchangeResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    x_device_fingerprint: Optional[str] = Header(None)
):
    """
    Rotate tokens using a valid refresh token.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY_REFRESH, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(status_code=401, detail="Could not validate refresh token")
    
    # v1.4.2: Check if refresh token is blacklisted
    if await redis_service.is_token_blacklisted(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )
    
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalars().first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Update last login/refresh time
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    # Check for user-wise expiry override
    expires_delta = None
    if user.access_token_expires_minutes:
        from datetime import timedelta
        expires_delta = timedelta(minutes=user.access_token_expires_minutes)

    return {
        "access_token": create_access_token(
            user.id, 
            expires_delta=expires_delta,
            fingerprint=x_device_fingerprint
        ),
        "refresh_token": create_refresh_token(
            user.id,
            fingerprint=x_device_fingerprint
        ),
        "token_type": "bearer",
    }


@router.post("/logout", response_model=StandardActionResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(reusable_oauth2),
    refresh_token: Optional[str] = Body(None, embed=True)
):
    """
    Revoke the current access token and optionally the refresh token.
    """
    # 1. Blacklist Access Token
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY_ACCESS, algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        now = datetime.now(timezone.utc).timestamp()
        ttl = int(exp - now)
        if ttl > 0:
            await redis_service.blacklist_token(token, ttl)
    except jwt.PyJWTError:
        pass

    # 2. Blacklist Refresh Token (if provided)
    if refresh_token:
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY_REFRESH, algorithms=[settings.ALGORITHM]
            )
            exp = payload.get("exp")
            now = datetime.now(timezone.utc).timestamp()
            ttl = int(exp - now)
            if ttl > 0:
                await redis_service.blacklist_token(refresh_token, ttl)
        except jwt.PyJWTError:
            pass
            
    return {"detail": "Revocation complete"}


@router.post("/revoke", response_model=StandardActionResponse)
async def revoke_token(
    token: str = Body(..., embed=True)
):
    """
    Standalone endpoint to revoke any valid token (Access or Refresh).
    """
    # Try Access Token first
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY_ACCESS, algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        now = datetime.now(timezone.utc).timestamp()
        ttl = int(exp - now)
        if ttl > 0:
            await redis_service.blacklist_token(token, ttl)
        return {"detail": "Access token revoked"}
    except jwt.PyJWTError:
        pass

    # Try Refresh Token
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY_REFRESH, algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        now = datetime.now(timezone.utc).timestamp()
        ttl = int(exp - now)
        if ttl > 0:
            await redis_service.blacklist_token(token, ttl)
        return {"detail": "Refresh token revoked"}
    except jwt.PyJWTError:
        pass

    raise HTTPException(status_code=400, detail="Invalid or already expired token")


@router.get("/blacklist", response_model=Any)
async def get_blacklist_items(
    current_user: User = Depends(get_current_user)
):
    """
    List all blacklisted tokens and their TTL. (Admin Only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    if not redis_service.redis_client:
        return {"detail": "Redis is not connected", "items": []}

    keys = await redis_service.redis_client.keys("blacklist:*")  # nosec B608
    items = []
    for key in keys:
        ttl = await redis_service.redis_client.ttl(key)
        # Return masked token for security
        masked_key = f"{key[:20]}...{key[-10:]}" if len(key) > 30 else key
        items.append({"id": masked_key, "ttl": ttl})

    return {"total": len(items), "items": items}



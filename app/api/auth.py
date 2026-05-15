from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt
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
    form_data: OAuth2PasswordRequestForm = Depends()
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

    # Create tokens with potential user-wise expiry override
    expires_delta = None
    if user.access_token_expires_minutes:
        from datetime import timedelta
        expires_delta = timedelta(minutes=user.access_token_expires_minutes)

    return {
        "access_token": create_access_token(user.id, expires_delta=expires_delta),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=TokenExchangeResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
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
    
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalars().first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Check for user-wise expiry override
    expires_delta = None
    if user.access_token_expires_minutes:
        from datetime import timedelta
        expires_delta = timedelta(minutes=user.access_token_expires_minutes)

    return {
        "access_token": create_access_token(user.id, expires_delta=expires_delta),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/logout", response_model=StandardActionResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(reusable_oauth2)
):
    """
    Revoke the current access token using Redis blacklisting.
    """
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
        pass # Token already invalid
        
    return {"detail": "Revocation complete"}


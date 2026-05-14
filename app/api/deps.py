from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.redis_service import redis_service

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    Zero-Trust Dependency: Validates JWT and checks Redis blacklist.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY_ACCESS, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # v1.4.2 Requirement: Explicit structural attribute check
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for this operation",
            )
            
        # Zero-Trust: Check Redis Blacklist
        # We use 'sub' as the JTI or just the whole token as a key if JTI isn't used.
        # However, the spec mentions "token fingerprint". I'll use the whole token or its hash.
        # For simplicity and exactness, I'll use the JTI if available, else the token itself.
        if await redis_service.is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

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
    try:
        print(f"DEBUG: Validating token...")
        payload = jwt.decode(
            token, settings.SECRET_KEY_ACCESS, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
            
        print(f"DEBUG: Checking Redis blacklist for token...")
        if await redis_service.is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked",
            )

    except Exception as e:
        print(f"DEBUG: Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )
    
    print(f"DEBUG: Fetching user {token_data.sub} from DB...")
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalars().first()
    
    if not user:
        print(f"DEBUG: User {token_data.sub} not found in DB.")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"DEBUG: User {user.email} authenticated successfully.")
    return user

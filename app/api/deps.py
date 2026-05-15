from typing import Generator, Optional
import hashlib
from fastapi import Depends, HTTPException, status, Header
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
    token: str = Depends(reusable_oauth2),
    x_device_fingerprint: Optional[str] = Header(None)
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
                detail="Token has been revoked",
            )
            
        # --- PHASE 2: Device Fingerprinting Validation ---
        if token_data.fpt:
            if not x_device_fingerprint:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Device signature required",
                )
            
            current_fpt_hash = hashlib.sha256(x_device_fingerprint.encode()).hexdigest()
            if current_fpt_hash != token_data.fpt:
                print(f"SECURITY ALERT: Fingerprint mismatch! Auto-revoking token.")
                # Force instant revocation for security breach
                from datetime import datetime, timezone
                exp = payload.get("exp")
                if exp:
                    now = datetime.now(timezone.utc).timestamp()
                    ttl = int(exp - now)
                    if ttl > 0:
                        await redis_service.blacklist_token(token, ttl)
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Identity Drift Detected: Device signature mismatch",
                )

    except HTTPException:
        raise
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    except Exception as e:
        print(f"DEBUG: Unexpected error during token validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Internal authentication error",
        )
    
    print(f"DEBUG: Fetching user {token_data.sub} from DB...")
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalars().first()
    
    if not user:
        print(f"DEBUG: User {token_data.sub} not found in DB.")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"DEBUG: User {user.email} authenticated successfully.")
    return user

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRegistrationResponse

router = APIRouter()

@router.get("/me", response_model=UserRegistrationResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Fetch the protected user profile metrics cleanly.
    """
    return current_user

@router.get("/", response_model=List[UserRegistrationResponse])
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all users. (Admin Only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    result = await db.execute(select(User))
    return result.scalars().all()

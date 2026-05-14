from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserRegistrationResponse

router = APIRouter()

@router.get("/me", response_model=UserRegistrationResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Fetch the protected user profile metrics cleanly.
    """
    return current_user

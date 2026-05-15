from typing import List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRegistrationResponse, SystemStatsResponse
from app.schemas.msg import StandardActionResponse
from app.services.redis_service import redis_service

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
    print(f"DEBUG: Admin {current_user.email} is fetching user list...")
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        print(f"DEBUG: Found {len(users)} users in database.")
        return users
    except Exception as e:
        print(f"DEBUG: Error fetching users from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@router.patch("/{user_id}/policy", response_model=UserRegistrationResponse)
async def update_user_policy(
    user_id: int,
    expires_minutes: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update token expiry policy for a specific user. (Admin Only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.access_token_expires_minutes = expires_minutes
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/policy/bulk", response_model=StandardActionResponse)
async def bulk_update_user_policy(
    expires_minutes: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update token expiry policy for ALL users. (Admin Only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    from sqlalchemy import update
    await db.execute(
        update(User).values(access_token_expires_minutes=expires_minutes)
    )
    await db.commit()
    return {"detail": f"Global policy enforced: {expires_minutes}m for all accounts."}

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch high-level system vitals and security metrics.
    Only accessible by Superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 1. Total & Admin Stats
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    admin_users_result = await db.execute(select(func.count(User.id)).where(User.is_superuser == True))
    admin_count = admin_users_result.scalar() or 0
    
    admin_concentration = (admin_count / total_users * 100) if total_users > 0 else 0

    # 2. Avg TTL Policy
    avg_ttl_result = await db.execute(select(func.avg(User.access_token_expires_minutes)))
    avg_session_policy = float(avg_ttl_result.scalar() or 15.0)

    # 3. New Arrivals (24h)
    time_24h_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    new_users_result = await db.execute(select(func.count(User.id)).where(User.created_at >= time_24h_ago))
    new_arrivals_24h = new_users_result.scalar() or 0

    # 4. Active Pulse (15m)
    time_15m_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
    active_users_result = await db.execute(select(func.count(User.id)).where(User.last_login_at >= time_15m_ago))
    active_pulse_15m = active_users_result.scalar() or 0

    # 5. Revocation Pulse (Redis)
    revocation_pulse = 0
    if redis_service.redis_client:
        try:
            # Note: This is an estimate of keys.
            revocation_pulse = await redis_service.redis_client.dbsize()
        except Exception:
            pass

    return {
        "total_users": total_users,
        "admin_count": admin_count,
        "admin_concentration": round(admin_concentration, 2),
        "new_arrivals_24h": new_arrivals_24h,
        "active_pulse_15m": active_pulse_15m,
        "avg_session_policy": round(avg_session_policy, 1),
        "revocation_pulse": revocation_pulse
    }

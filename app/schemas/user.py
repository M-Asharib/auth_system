from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr


class UserPolicyUpdate(BaseModel):
    expires_minutes: int = Field(..., gt=0, lt=10080)


class SystemStatsResponse(BaseModel):
    total_users: int
    admin_count: int
    admin_concentration: float
    new_arrivals_24h: int
    active_pulse_15m: int
    avg_session_policy: float
    revocation_pulse: int


class UserCreate(UserBase):
    password: str


class UserRegistrationResponse(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

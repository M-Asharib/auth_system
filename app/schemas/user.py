from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRegistrationResponse(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    access_token_expires_minutes: int | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

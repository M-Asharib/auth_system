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
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

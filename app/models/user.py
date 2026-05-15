from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    access_token_expires_minutes = Column(Integer, nullable=True) # User-wise override
    last_login_at = Column(DateTime(timezone=True), nullable=True) # For real-time monitoring
    created_at = Column(DateTime(timezone=True), server_default=func.now())

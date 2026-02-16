"""
User schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserUpdate(BaseModel):
    """Update user profile schema"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    phone: Optional[str] = None
    phone_verified: bool
    email: Optional[str] = None
    email_verified: bool
    telegram_user_id: Optional[str] = None
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


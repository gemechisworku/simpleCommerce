"""
User schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_serializer
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class AdminUserCreate(BaseModel):
    """Create user schema (admin)"""
    phone: str = Field(..., description="Phone number in E.164 format")
    email: Optional[EmailStr] = Field(None, description="Email address")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: str = Field(..., description="Role: sales or admin")


class AdminUserRoleUpdate(BaseModel):
    """Update user role schema"""
    role: str = Field(..., description="New role: customer, sales, or admin")


class _RoleMixin:
    """Serialize role to lowercase for API (frontend expects 'admin'|'sales'|'customer')."""
    @field_serializer("role")
    def serialize_role(self, v: Any) -> str:
        if hasattr(v, "value"):
            return getattr(v, "value", v).lower() if getattr(v, "value", v) else ""
        return str(v).lower() if v else ""
}


class UserListItemResponse(BaseModel, _RoleMixin):
    """User list item (for admin list)"""
    id: UUID
    phone: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserDetailResponse(BaseModel, _RoleMixin):
    """User detail response (includes orders count)"""
    id: UUID
    phone: Optional[str] = None
    phone_verified: bool
    email: Optional[str] = None
    email_verified: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    orders_count: int = 0
    recent_order_ids: list = []

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Update user profile schema"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel, _RoleMixin):
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


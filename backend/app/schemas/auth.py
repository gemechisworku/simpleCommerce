"""
Authentication schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class OTPRequest(BaseModel):
    """Request OTP schema"""
    phone: str = Field(..., description="Phone number in E.164 format")


class OTPVerify(BaseModel):
    """Verify OTP schema"""
    phone: str = Field(..., description="Phone number")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class EmailOTPRequest(BaseModel):
    """Request email OTP schema"""
    email: EmailStr = Field(..., description="Email address")


class EmailOTPVerify(BaseModel):
    """Verify email OTP schema"""
    email: EmailStr = Field(..., description="Email address")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")


class TelegramVerifyRequest(BaseModel):
    """Telegram WebApp initData verification request"""
    init_data: str = Field(..., description="Telegram WebApp initData string")


class LogoutRequest(BaseModel):
    """Logout request schema"""
    refresh_token: str = Field(..., description="Refresh token to revoke")


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds


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

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse


class OTPResponse(BaseModel):
    """OTP request response schema"""
    message: str
    expires_in: int  # seconds


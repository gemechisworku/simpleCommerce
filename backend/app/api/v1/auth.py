"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import BusinessRuleError
from app.core.config import settings
from app.utils.helpers import validate_phone
from app.utils.rate_limit import check_otp_rate_limit
from app.services.otp_delivery import is_sms_configured
from app.schemas.auth import (
    OTPRequest,
    OTPVerify,
    EmailOTPRequest,
    EmailOTPVerify,
    RefreshTokenRequest,
    TelegramVerifyRequest,
    LogoutRequest,
    LoginResponse,
    OTPResponse,
    TokenResponse
)
from app.schemas.common import ResponseModel
from app.services.auth.otp_service import (
    create_otp,
    verify_otp,
    get_or_create_user_by_phone,
    get_or_create_user_by_email
)
from app.services.auth.token_service import (
    create_tokens_for_user,
    refresh_access_token,
    revoke_refresh_token
)
from app.services.auth.telegram_service import get_or_create_user_by_telegram
from app.core.telegram import validate_telegram_init_data
from app.models.auth import OTPType, OTPPurpose
from app.core.exceptions import BusinessRuleError
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from typing import Optional
import secrets

router = APIRouter()


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request"""
    # Check for forwarded IP (from proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    if request.client:
        return request.client.host
    
    return None


@router.post("/otp/request", response_model=ResponseModel[OTPResponse], status_code=status.HTTP_200_OK)
async def request_otp(
    request_data: OTPRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Request OTP code via phone number (used when accessing outside Telegram).
    OTP is always sent via Telegram when possible: directly if the user has a linked account,
    or via a one-time "Open in Telegram" link for first-time users (open link → receive code in chat).
    """
    if not validate_phone(request_data.phone):
        raise BusinessRuleError("Invalid phone number format. Please use E.164 format (e.g., +251912345678)")
    ip_address = get_client_ip(request)
    check_otp_rate_limit(db, request_data.phone, ip_address)

    telegram_user_id: Optional[str] = None
    user = db.query(User).filter(User.phone == request_data.phone).first()
    if user and user.telegram_user_id:
        telegram_user_id = user.telegram_user_id

    can_deliver_via_telegram_link = bool(
        settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_USERNAME
    )
    can_deliver = (
        settings.ENVIRONMENT == "development"
        or telegram_user_id
        or is_sms_configured()
        or can_deliver_via_telegram_link
    )
    if not can_deliver:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "code": "OTP_DELIVERY_UNAVAILABLE",
                "message": "We can't send a code to this number yet. Configure TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_USERNAME, or an SMS provider.",
            },
        )

    otp = create_otp(
        db=db,
        identifier=request_data.phone,
        otp_type=OTPType.PHONE,
        purpose=OTPPurpose.LOGIN,
        ip_address=ip_address,
        telegram_user_id=telegram_user_id,
    )
    telegram_otp_link: Optional[str] = None
    if not telegram_user_id and can_deliver_via_telegram_link:
        token = secrets.token_urlsafe(32)
        otp.delivery_token = token
        db.commit()
        telegram_otp_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME.strip()}?start=otp_{token}"

    return ResponseModel(data=OTPResponse(
        message="OTP sent successfully",
        expires_in=settings.OTP_EXPIRY_MINUTES * 60,
        telegram_otp_link=telegram_otp_link,
    ))


@router.post("/otp/verify", response_model=ResponseModel[LoginResponse], status_code=status.HTTP_200_OK)
async def verify_otp_and_login(
    request_data: OTPVerify,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify OTP code and receive JWT tokens
    """
    # Verify OTP
    otp = verify_otp(
        db=db,
        identifier=request_data.phone,
        code=request_data.code,
        otp_type=OTPType.PHONE,
        purpose=OTPPurpose.LOGIN
    )
    
    # Get or create user
    user = get_or_create_user_by_phone(db, request_data.phone)
    
    # Create tokens
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    
    access_token, refresh_token, _ = create_tokens_for_user(
        db=db,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return ResponseModel(data=LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    ))


@router.post("/email/request", response_model=ResponseModel[OTPResponse], status_code=status.HTTP_200_OK)
async def request_email_otp(
    request_data: EmailOTPRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Request OTP code via email
    """
    ip_address = get_client_ip(request)
    
    # Create OTP
    otp = create_otp(
        db=db,
        identifier=request_data.email,
        otp_type=OTPType.EMAIL,
        purpose=OTPPurpose.LOGIN,
        ip_address=ip_address
    )
    
    return ResponseModel(data=OTPResponse(
        message="OTP sent to email",
        expires_in=settings.OTP_EXPIRY_MINUTES * 60
    ))


@router.post("/email/verify", response_model=ResponseModel[LoginResponse], status_code=status.HTTP_200_OK)
async def verify_email_otp_and_login(
    request_data: EmailOTPVerify,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify email OTP code and receive JWT tokens
    """
    # Verify OTP
    otp = verify_otp(
        db=db,
        identifier=request_data.email,
        code=request_data.code,
        otp_type=OTPType.EMAIL,
        purpose=OTPPurpose.LOGIN
    )
    
    # Get or create user
    user = get_or_create_user_by_email(db, request_data.email)
    
    # Create tokens
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    
    access_token, refresh_token, _ = create_tokens_for_user(
        db=db,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return ResponseModel(data=LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    ))


@router.post("/telegram/verify", response_model=ResponseModel[LoginResponse], status_code=status.HTTP_200_OK)
async def verify_telegram_and_login(
    request_data: TelegramVerifyRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify Telegram WebApp initData and log in (or create telegram-only account).
    Used when the app is opened as a Telegram Mini App.
    """
    payload = validate_telegram_init_data(request_data.init_data)
    if not payload:
        raise BusinessRuleError("Invalid or expired Telegram initData. Please open the app from Telegram again.")

    tg_user = payload["user"]
    telegram_user_id = str(tg_user.get("id"))
    if not telegram_user_id:
        raise BusinessRuleError("Invalid Telegram user data.")

    user = get_or_create_user_by_telegram(
        db=db,
        telegram_user_id=telegram_user_id,
        telegram_username=tg_user.get("username"),
        first_name=tg_user.get("first_name"),
        last_name=tg_user.get("last_name"),
    )

    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    access_token, refresh_token, _ = create_tokens_for_user(
        db=db,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return ResponseModel(data=LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    ))


@router.post("/refresh", response_model=ResponseModel[TokenResponse], status_code=status.HTTP_200_OK)
async def refresh_token(
    request_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    access_token, refresh_token, _ = refresh_access_token(
        db=db,
        refresh_token=request_data.refresh_token
    )
    
    return ResponseModel(data=TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    ))


@router.post("/logout", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK)
async def logout(
    request_data: LogoutRequest,
    db: Session = Depends(get_db)
):
    """
    Logout and revoke refresh token
    """
    revoke_refresh_token(db, request_data.refresh_token)
    
    return ResponseModel(data={"message": "Logged out successfully"})




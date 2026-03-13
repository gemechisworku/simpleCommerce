"""
OTP service for generating and verifying OTP codes
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.auth import OTPCode, OTPType, OTPPurpose
from app.models.user import User, UserRole
from app.utils.helpers import generate_otp, validate_phone, validate_email
from app.core.config import settings
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.utils.rate_limit import check_otp_rate_limit
from app.services.otp_delivery import send_otp_sms, send_otp_email, send_otp_telegram
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def create_otp(
    db: Session,
    identifier: str,
    otp_type: OTPType,
    purpose: OTPPurpose = OTPPurpose.LOGIN,
    ip_address: Optional[str] = None,
    telegram_user_id: Optional[str] = None,
) -> OTPCode:
    """
    Create and store OTP code.

    If telegram_user_id is provided (e.g. from Mini App init_data), OTP is sent via Telegram
    when TELEGRAM_BOT_TOKEN is set; otherwise falls back to SMS/email or log-only.
    """
    # Validate identifier format
    if otp_type == OTPType.PHONE:
        if not validate_phone(identifier):
            raise BusinessRuleError("Invalid phone number format. Please use E.164 format (e.g., +251912345678)")
    elif otp_type == OTPType.EMAIL:
        if not validate_email(identifier):
            raise BusinessRuleError("Invalid email format")
    
    # Check rate limiting
    check_otp_rate_limit(db, identifier, ip_address)
    
    # Generate OTP code
    code = generate_otp(length=6)
    
    # Calculate expiration (5 minutes from now)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    
    # Create OTP record
    otp = OTPCode(
        identifier=identifier,
        code=code,
        type=otp_type,
        purpose=purpose,
        expires_at=expires_at,
        ip_address=ip_address
    )
    
    db.add(otp)
    db.commit()
    db.refresh(otp)
    
    # Delivery: prefer Telegram if telegram_user_id provided; else dev log or SMS/email
    if settings.ENVIRONMENT == "development":
        logger.info(f"OTP for {identifier}: {code} (expires at {expires_at})")
    else:
        sent = False
        if telegram_user_id:
            sent = send_otp_telegram(telegram_user_id, code)
        if not sent and otp_type == OTPType.PHONE:
            sent = send_otp_sms(identifier, code)
        if not sent and otp_type == OTPType.EMAIL:
            sent = send_otp_email(identifier, code)
        if not sent:
            logger.info(
                "OTP generated for %s (not sent: use Telegram Mini App with init_data, or set OTP_SMS_PROVIDER)",
                identifier,
            )
    return otp


def verify_otp(
    db: Session,
    identifier: str,
    code: str,
    otp_type: OTPType,
    purpose: OTPPurpose = OTPPurpose.LOGIN
) -> OTPCode:
    """
    Verify OTP code
    
    Args:
        db: Database session
        identifier: Phone number or email
        code: OTP code to verify
        otp_type: Type of OTP
        purpose: Purpose of OTP
        
    Returns:
        OTPCode object if valid
        
    Raises:
        NotFoundError: If OTP not found
        BusinessRuleError: If OTP expired or already used
    """
    # Find OTP code
    otp = db.query(OTPCode).filter(
        and_(
            OTPCode.identifier == identifier,
            OTPCode.code == code,
            OTPCode.type == otp_type,
            OTPCode.purpose == purpose,
            OTPCode.used_at.is_(None)  # Not used yet
        )
    ).order_by(OTPCode.created_at.desc()).first()
    
    if not otp:
        raise NotFoundError("Invalid OTP code")
    
    # Check if expired
    if datetime.now(timezone.utc) > otp.expires_at:
        raise BusinessRuleError("OTP expired. Please request a new one.")
    
    # Check if already used
    if otp.used_at is not None:
        raise BusinessRuleError("OTP already used")
    
    # Mark as used
    otp.used_at = datetime.now(timezone.utc)
    db.commit()
    
    return otp


def get_or_create_user_by_phone(db: Session, phone: str) -> User:
    """
    Get existing user by phone or create new one
    
    Args:
        db: Database session
        phone: Phone number
        
    Returns:
        User object
    """
    user = db.query(User).filter(User.phone == phone).first()
    
    if not user:
        # Create new user
        user = User(
            phone=phone,
            phone_verified=True,
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user with phone: {phone}")
    else:
        # Update phone verification if not already verified
        if not user.phone_verified:
            user.phone_verified = True
            db.commit()
            db.refresh(user)
    
    return user


def get_or_create_user_by_email(db: Session, email: str) -> User:
    """
    Get existing user by email or create new one
    
    Args:
        db: Database session
        email: Email address
        
    Returns:
        User object
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Create new user
        user = User(
            email=email,
            email_verified=True,
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user with email: {email}")
    else:
        # Update email verification if not already verified
        if not user.email_verified:
            user.email_verified = True
            db.commit()
            db.refresh(user)
    
    return user


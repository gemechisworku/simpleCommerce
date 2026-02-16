"""
Rate limiting utilities
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.auth import OTPCode, OTPType
from app.core.exceptions import RateLimitError
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def check_otp_rate_limit(
    db: Session,
    identifier: str,
    ip_address: Optional[str] = None,
    max_per_identifier: Optional[int] = None,
    max_per_ip: Optional[int] = None,
    window_minutes: Optional[int] = None
) -> None:
    """
    Check rate limiting for OTP requests
    
    Args:
        db: Database session
        identifier: Phone number or email
        ip_address: Client IP address
        max_per_identifier: Max requests per identifier in time window (uses config if None)
        max_per_ip: Max requests per IP in time window (uses config if None)
        window_minutes: Time window in minutes (uses config if None)
        
    Raises:
        RateLimitError: If rate limit exceeded
    """
    # Use config values if not provided
    window_minutes = window_minutes or settings.OTP_RATE_LIMIT_WINDOW_MINUTES
    max_per_identifier = max_per_identifier or settings.OTP_RATE_LIMIT_MAX_PER_IDENTIFIER
    max_per_ip = max_per_ip or settings.OTP_RATE_LIMIT_MAX_PER_IP
    
    window_start = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    
    # Determine OTP type enum based on identifier
    otp_type = OTPType.PHONE if '@' not in identifier else OTPType.EMAIL
    
    # Check requests per identifier
    identifier_count = db.query(func.count(OTPCode.id)).filter(
        and_(
            OTPCode.identifier == identifier,
            OTPCode.created_at >= window_start,
            OTPCode.type == otp_type
        )
    ).scalar()
    
    if identifier_count >= max_per_identifier:
        raise RateLimitError(
            f"Too many OTP requests. Please wait {window_minutes} minutes before requesting again."
        )
    
    # Check requests per IP (if provided)
    if ip_address:
        ip_count = db.query(func.count(OTPCode.id)).filter(
            and_(
                OTPCode.ip_address == ip_address,
                OTPCode.created_at >= window_start
            )
        ).scalar()
        
        if ip_count >= max_per_ip:
            raise RateLimitError(
                f"Too many OTP requests from this IP. Please wait {window_minutes} minutes before requesting again."
            )


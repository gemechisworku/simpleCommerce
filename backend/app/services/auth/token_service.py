"""
Token service for JWT token management
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User
from app.models.auth import RefreshToken
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def create_tokens_for_user(
    db: Session,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Tuple[str, str, RefreshToken]:
    """
    Create access and refresh tokens for user
    
    Args:
        db: Database session
        user: User object
        ip_address: Client IP address
        user_agent: Client user agent
        
    Returns:
        Tuple of (access_token, refresh_token, refresh_token_record)
    """
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value.lower()}
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # Store refresh token in database
    expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(refresh_token_record)
    db.commit()
    db.refresh(refresh_token_record)
    
    return access_token, refresh_token, refresh_token_record


def refresh_access_token(
    db: Session,
    refresh_token: str
) -> Tuple[str, str, RefreshToken]:
    """
    Refresh access token using refresh token
    
    Args:
        db: Database session
        refresh_token: Refresh token string
        
    Returns:
        Tuple of (new_access_token, refresh_token, refresh_token_record)
        
    Raises:
        AuthenticationError: If refresh token is invalid
    """
    # Verify refresh token
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise AuthenticationError("Invalid refresh token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")
    
    # Find refresh token in database
    token_record = db.query(RefreshToken).filter(
        and_(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow()
        )
    ).first()
    
    if not token_record:
        raise AuthenticationError("Invalid or expired refresh token")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    
    # Create new access token
    new_access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value.lower()}
    )
    
    # Optionally rotate refresh token (for security)
    # For now, we'll return the same refresh token
    # In production, you might want to rotate it
    
    return new_access_token, refresh_token, token_record


def revoke_refresh_token(
    db: Session,
    refresh_token: str
) -> None:
    """
    Revoke a refresh token (logout)
    
    Args:
        db: Database session
        refresh_token: Refresh token to revoke
    """
    token_record = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()
    
    if token_record and not token_record.revoked_at:
        token_record.revoked_at = datetime.utcnow()
        db.commit()
        logger.info(f"Revoked refresh token for user: {token_record.user_id}")


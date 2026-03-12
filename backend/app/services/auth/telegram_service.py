"""
Telegram authentication: validate initData and get/create user by Telegram identity.
"""
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.telegram import validate_telegram_init_data
from app.core.exceptions import BusinessRuleError
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_or_create_user_by_telegram(
    db: Session,
    telegram_user_id: str,
    telegram_username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> User:
    """
    Get existing user by telegram_user_id or create new one (telegram-only account).

    Args:
        db: Database session
        telegram_user_id: Telegram user ID (string to match model)
        telegram_username: Telegram username
        first_name: First name from Telegram
        last_name: Last name from Telegram

    Returns:
        User object
    """
    user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()

    if not user:
        user = User(
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            first_name=first_name,
            last_name=last_name,
            phone=None,
            phone_verified=False,
            email=None,
            email_verified=False,
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user from Telegram: telegram_user_id={telegram_user_id}")
    else:
        # Update Telegram profile if changed
        updated = False
        if telegram_username is not None and user.telegram_username != telegram_username:
            user.telegram_username = telegram_username
            updated = True
        if first_name is not None and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name is not None and user.last_name != last_name:
            user.last_name = last_name
            updated = True
        if updated:
            db.commit()
            db.refresh(user)

    return user

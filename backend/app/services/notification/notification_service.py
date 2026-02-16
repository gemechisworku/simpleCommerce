"""
Notification service
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from app.models.notification import Notification, NotificationType
from app.core.exceptions import NotFoundError
import logging

logger = logging.getLogger(__name__)


def create_notification(
    db: Session,
    user_id: UUID,
    type: NotificationType,
    title: str,
    message: str,
    link: Optional[str] = None
) -> Notification:
    """
    Create a notification
    
    Args:
        db: Database session
        user_id: User ID to notify
        type: Notification type
        title: Notification title
        message: Notification message
        link: Optional link URL
        
    Returns:
        Created Notification object
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        link=link,
        is_read=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    logger.info(f"Created notification for user {user_id}: {title}")
    return notification


def list_user_notifications(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
    is_read: Optional[bool] = None
) -> Tuple[List[Notification], int]:
    """
    List notifications for a user
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_read: Filter by read status
        
    Returns:
        Tuple of (notifications list, total count)
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    total = query.count()
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return notifications, total


def mark_notifications_as_read(
    db: Session,
    user_id: UUID,
    notification_ids: List[int]
) -> int:
    """
    Mark notifications as read
    
    Args:
        db: Database session
        user_id: User ID
        notification_ids: List of notification IDs
        
    Returns:
        Number of notifications marked as read
    """
    count = db.query(Notification).filter(
        and_(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    ).update({"is_read": True}, synchronize_session=False)
    
    db.commit()
    
    logger.info(f"Marked {count} notifications as read for user {user_id}")
    return count


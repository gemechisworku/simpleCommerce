"""
Notification endpoints
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationMarkReadRequest
from app.schemas.common import ResponseModel, PaginatedResponse, PaginationMeta
from app.services.notification import list_user_notifications, mark_notifications_as_read, get_unread_count
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=PaginatedResponse[NotificationResponse], status_code=status.HTTP_200_OK)
async def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List notifications for current user
    
    Requires authentication.
    """
    skip = (page - 1) * per_page
    notifications, total = list_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=per_page,
        is_read=is_read
    )
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        data=[NotificationResponse.model_validate(n) for n in notifications],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )


@router.post("/mark-read", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK)
async def mark_notifications_as_read_endpoint(
    read_data: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark notifications as read
    
    Requires authentication.
    """
    count = mark_notifications_as_read(
        db=db,
        user_id=current_user.id,
        notification_ids=read_data.notification_ids
    )
    
    return ResponseModel(data={"message": f"{count} notifications marked as read"})


@router.get("/unread-count", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK)
async def get_unread_count_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications

    Requires authentication.
    """
    count = get_unread_count(db=db, user_id=current_user.id)
    return ResponseModel(data={"count": count})


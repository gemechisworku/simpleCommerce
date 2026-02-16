"""
Notification schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class NotificationResponse(BaseModel):
    """Notification response schema"""
    id: int
    user_id: UUID
    type: str
    title: str
    message: str
    link: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationMarkReadRequest(BaseModel):
    """Mark notification as read request schema"""
    notification_ids: list[int] = Field(..., min_length=1, description="Notification IDs to mark as read")


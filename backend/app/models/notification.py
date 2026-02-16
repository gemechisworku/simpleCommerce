"""
Notification model
"""
from sqlalchemy import Column, String, Text, Boolean, BigInteger, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class NotificationType(str, enum.Enum):
    """Notification type enum"""
    PAYMENT_APPROVED = "PAYMENT_APPROVED"
    PAYMENT_REJECTED = "PAYMENT_REJECTED"
    PAYMENT_RESUBMIT_REQUESTED = "PAYMENT_RESUBMIT_REQUESTED"
    ORDER_STATUS_UPDATED = "ORDER_STATUS_UPDATED"
    ORDER_DISPATCHED = "ORDER_DISPATCHED"
    ORDER_DELIVERED = "ORDER_DELIVERED"
    NEW_ORDER = "NEW_ORDER"
    NEW_PAYMENT_SUBMITTED = "NEW_PAYMENT_SUBMITTED"


class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(NotificationType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    related_order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=True, index=True)
    related_payment_id = Column(BigInteger, ForeignKey("payments.id", ondelete="CASCADE"), nullable=True, index=True)
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="notifications")
    related_order = relationship("Order")
    related_payment = relationship("Payment")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"


"""
Payment models
"""
from sqlalchemy import Column, String, Text, Boolean, BigInteger, Integer, ForeignKey, DateTime, Numeric, CheckConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class PaymentMethodType(str, enum.Enum):
    """Payment method type enum"""
    BANK_TRANSFER = "BANK_TRANSFER"
    MOBILE_MONEY = "MOBILE_MONEY"
    OTHER = "OTHER"


class PaymentStatus(str, enum.Enum):
    """Payment status enum"""
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESUBMIT_REQUESTED = "resubmit_requested"


class PaymentMethod(Base):
    """Payment method model"""
    __tablename__ = "payment_methods"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(SQLEnum(PaymentMethodType), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    account_identifier = Column(String(100), nullable=False)
    account_holder = Column(String(100), nullable=False)
    instructions = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    payments = relationship("Payment", back_populates="method")

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, name={self.name}, type={self.type})>"


class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    method_id = Column(BigInteger, ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False, index=True)
    submitted_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount_declared = Column(Numeric(10, 2), nullable=True)
    reference_text = Column(String(200), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    screenshot_url = Column(String(500), nullable=False)
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.SUBMITTED, index=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="payments")
    method = relationship("PaymentMethod", back_populates="payments")
    submitted_by = relationship("User", foreign_keys=[submitted_by_user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    # Constraints
    __table_args__ = (
        CheckConstraint("amount_declared >= 0", name="check_amount_declared_non_negative"),
    )

    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status})>"


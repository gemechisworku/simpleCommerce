"""
Order models
"""
from sqlalchemy import Column, String, Text, Boolean, BigInteger, ForeignKey, DateTime, Date, Numeric, Integer, CheckConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enum"""
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAYMENT_SUBMITTED = "PAYMENT_SUBMITTED"
    PAYMENT_RESUBMIT_REQUESTED = "PAYMENT_RESUBMIT_REQUESTED"
    PAYMENT_REJECTED = "PAYMENT_REJECTED"
    PAID = "PAID"
    PACKING = "PACKING"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(Base):
    """Order model"""
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_number = Column(String(20), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(SQLEnum(OrderStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=OrderStatus.PENDING_PAYMENT, index=True)
    subtotal = Column(Numeric(10, 2), nullable=False)
    delivery_fee = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    delivery_zone_id = Column(BigInteger, ForeignKey("delivery_zones.id", ondelete="SET NULL"), nullable=True, index=True)
    delivery_address = Column(Text, nullable=False)
    recipient_name = Column(String(100), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    delivery_instructions = Column(Text, nullable=True)
    expected_delivery_from = Column(Date, nullable=True)
    expected_delivery_to = Column(Date, nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="orders")
    delivery_zone = relationship("DeliveryZone", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="check_subtotal_non_negative"),
        CheckConstraint("delivery_fee >= 0", name="check_delivery_fee_non_negative"),
        CheckConstraint("total >= 0", name="check_total_non_negative"),
    )

    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"


class OrderItem(Base):
    """Order item model"""
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    variant_id = Column(BigInteger, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True)
    product_name = Column(String(200), nullable=False)
    variant_label = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")

    # Constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="check_unit_price_non_negative"),
        CheckConstraint("line_total >= 0", name="check_line_total_non_negative"),
    )

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_name={self.product_name}, quantity={self.quantity})>"


class OrderStatusHistory(Base):
    """Order status history model"""
    __tablename__ = "order_status_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status = Column(SQLEnum(OrderStatus, values_callable=lambda x: [e.value for e in x]), nullable=True)
    new_status = Column(SQLEnum(OrderStatus, values_callable=lambda x: [e.value for e in x]), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    order = relationship("Order", back_populates="status_history")
    actor = relationship("User")

    def __repr__(self):
        return f"<OrderStatusHistory(id={self.id}, order_id={self.order_id}, old_status={self.old_status}, new_status={self.new_status})>"


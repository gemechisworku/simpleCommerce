"""
Delivery zone model
"""
from sqlalchemy import Column, String, Text, Boolean, BigInteger, Numeric, Integer, CheckConstraint, DateTime
from sqlalchemy.sql import func
from app.models.base import Base


class DeliveryZone(Base):
    """Delivery zone model"""
    __tablename__ = "delivery_zones"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    fee = Column(Numeric(10, 2), nullable=False)
    eta_min_days = Column(Integer, nullable=False, default=1)
    eta_max_days = Column(Integer, nullable=False, default=2)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("fee >= 0", name="check_fee_non_negative"),
        CheckConstraint("eta_min_days >= 0", name="check_eta_min_non_negative"),
        CheckConstraint("eta_max_days >= eta_min_days", name="check_eta_max_gte_min"),
    )

    def __repr__(self):
        return f"<DeliveryZone(id={self.id}, name={self.name}, fee={self.fee})>"


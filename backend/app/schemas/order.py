"""
Order schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID


# Order Item Schemas
class OrderItemCreate(BaseModel):
    """Create order item schema"""
    variant_id: int = Field(..., description="Product variant ID")
    quantity: int = Field(..., gt=0, description="Quantity")


class OrderItemResponse(BaseModel):
    """Order item response schema"""
    id: int
    order_id: int
    product_id: int
    variant_id: Optional[int] = None
    product_name: str
    variant_label: Optional[str] = None
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


# Order Status History Schema
class OrderStatusHistoryResponse(BaseModel):
    """Order status history response schema"""
    id: int
    order_id: int
    old_status: Optional[str] = None
    new_status: str
    actor_user_id: Optional[UUID] = None
    note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Order Schemas
class OrderCreate(BaseModel):
    """Create order schema"""
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Order items")
    delivery_zone_id: int = Field(..., description="Delivery zone ID")
    delivery_address: str = Field(..., min_length=10, description="Delivery address")
    recipient_name: str = Field(..., max_length=100, description="Recipient name")
    recipient_phone: str = Field(..., max_length=20, description="Recipient phone number")
    delivery_instructions: Optional[str] = Field(None, description="Delivery instructions")


class OrderResponse(BaseModel):
    """Order response schema"""
    id: int
    order_number: str
    user_id: UUID
    status: str
    subtotal: Decimal
    delivery_fee: Decimal
    total: Decimal
    delivery_zone_id: Optional[int] = None
    delivery_address: str
    recipient_name: str
    recipient_phone: str
    delivery_instructions: Optional[str] = None
    expected_delivery_from: Optional[date] = None
    expected_delivery_to: Optional[date] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    status_history: List[OrderStatusHistoryResponse] = []

    model_config = {"from_attributes": True}


class OrderListItemResponse(BaseModel):
    """Order list item response schema (simplified)"""
    id: int
    order_number: str
    status: str
    total: Decimal
    created_at: datetime
    expected_delivery_from: Optional[date] = None
    expected_delivery_to: Optional[date] = None

    model_config = {"from_attributes": True}


class OrderCancelRequest(BaseModel):
    """Cancel order request schema"""
    reason: Optional[str] = Field(None, max_length=500, description="Cancellation reason")


class OrderStatusUpdateRequest(BaseModel):
    """Update order status request schema"""
    status: str = Field(..., description="New order status")
    note: Optional[str] = Field(None, max_length=500, description="Status change note")


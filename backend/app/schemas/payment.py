"""
Payment schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID


# Payment Method Schemas
class PaymentMethodCreate(BaseModel):
    """Create payment method schema"""
    type: str = Field(..., description="Payment method type")
    name: str = Field(..., max_length=100, description="Payment method name")
    account_identifier: str = Field(..., max_length=100, description="Account number/identifier")
    account_holder: str = Field(..., max_length=100, description="Account holder name")
    instructions: Optional[str] = Field(None, description="Payment instructions")
    is_active: bool = Field(True, description="Active status")
    sort_order: int = Field(0, ge=0, description="Display sort order")


class PaymentMethodUpdate(BaseModel):
    """Update payment method schema"""
    name: Optional[str] = Field(None, max_length=100)
    account_identifier: Optional[str] = Field(None, max_length=100)
    account_holder: Optional[str] = Field(None, max_length=100)
    instructions: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class PaymentMethodResponse(BaseModel):
    """Payment method response schema"""
    id: int
    type: str
    name: str
    account_identifier: str
    account_holder: str
    instructions: Optional[str] = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Payment Schemas
class PaymentSubmitRequest(BaseModel):
    """Submit payment request schema"""
    order_id: int = Field(..., description="Order ID")
    method_id: int = Field(..., description="Payment method ID")
    amount_declared: Optional[Decimal] = Field(None, ge=0, description="Declared payment amount")
    reference_text: Optional[str] = Field(None, max_length=200, description="Payment reference/transaction ID")
    paid_at: Optional[datetime] = Field(None, description="Payment date/time")


class PaymentResponse(BaseModel):
    """Payment response schema"""
    id: int
    order_id: int
    method_id: int
    submitted_by_user_id: UUID
    amount_declared: Optional[Decimal] = None
    reference_text: Optional[str] = None
    paid_at: Optional[datetime] = None
    screenshot_url: str
    status: str
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    review_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentReviewRequest(BaseModel):
    """Payment review request schema"""
    note: Optional[str] = Field(None, max_length=500, description="Review note")


class PaymentRejectRequest(BaseModel):
    """Payment reject request schema"""
    reason: str = Field(..., min_length=10, max_length=500, description="Rejection reason")


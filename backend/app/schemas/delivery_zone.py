"""
Delivery zone schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime, date


class DeliveryZoneCreate(BaseModel):
    """Create delivery zone schema"""
    name: str = Field(..., max_length=100, description="Zone name")
    description: Optional[str] = Field(None, description="Zone description")
    fee: Decimal = Field(..., ge=0, description="Delivery fee")
    eta_min_days: int = Field(..., ge=0, description="Minimum delivery days")
    eta_max_days: int = Field(..., ge=1, description="Maximum delivery days")
    is_active: bool = Field(True, description="Active status")


class DeliveryZoneUpdate(BaseModel):
    """Update delivery zone schema"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    fee: Optional[Decimal] = Field(None, ge=0)
    eta_min_days: Optional[int] = Field(None, ge=0)
    eta_max_days: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class DeliveryZoneResponse(BaseModel):
    """Delivery zone response schema"""
    id: int
    name: str
    description: Optional[str] = None
    fee: Decimal
    eta_min_days: int
    eta_max_days: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeliveryFeeCalculationResponse(BaseModel):
    """Delivery fee calculation response schema"""
    zone_id: int
    zone_name: str
    fee: Decimal
    eta_min_days: int
    eta_max_days: int
    expected_delivery_from: date
    expected_delivery_to: date


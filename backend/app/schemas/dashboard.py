"""
Dashboard schemas
"""
from pydantic import BaseModel
from typing import Dict, List

from app.schemas.order import OrderListItemResponse


class DashboardResponse(BaseModel):
    """Dashboard metrics response"""
    orders_today: int
    pending_payments_count: int
    orders_by_status: Dict[str, int]
    revenue_today: float
    recent_orders: List[OrderListItemResponse]

"""
Admin dashboard endpoints
"""
from fastapi import APIRouter, Depends, status

from app.core.database import get_db
from app.api.dependencies import require_sales_or_admin
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.schemas.common import ResponseModel
from app.schemas.order import OrderListItemResponse
from app.services.dashboard import get_dashboard_metrics
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=ResponseModel[DashboardResponse], status_code=status.HTTP_200_OK)
async def get_dashboard(
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get dashboard metrics

    Returns orders today, pending payments count, orders by status,
    revenue today, and recent orders.

    Requires sales or admin role.
    """
    metrics = get_dashboard_metrics(db)

    # Serialize recent orders
    recent_orders_data = [
        OrderListItemResponse.model_validate(o) for o in metrics["recent_orders"]
    ]

    return ResponseModel(
        data=DashboardResponse(
            orders_today=metrics["orders_today"],
            pending_payments_count=metrics["pending_payments_count"],
            orders_by_status=metrics["orders_by_status"],
            revenue_today=metrics["revenue_today"],
            recent_orders=recent_orders_data,
        )
    )

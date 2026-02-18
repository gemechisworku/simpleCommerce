"""
Dashboard service for admin metrics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List

from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus


def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
    """
    Get dashboard metrics for admin/sales users

    Returns:
        Dictionary with:
        - orders_today: Count of orders created today
        - pending_payments_count: Count of payments with submitted status
        - orders_by_status: Dict of status -> count
        - revenue_today: Sum of order totals for payments approved today
        - recent_orders: Last 10 orders
    """
    today = date.today()

    # Orders created today
    orders_today = (
        db.query(func.count(Order.id))
        .filter(func.date(Order.created_at) == today)
        .filter(Order.status != OrderStatus.CANCELLED)
        .scalar()
        or 0
    )

    # Pending payments (submitted status)
    pending_payments_count = (
        db.query(func.count(Payment.id))
        .filter(Payment.status == PaymentStatus.SUBMITTED)
        .scalar()
        or 0
    )

    # Orders by status (excluding cancelled for "active" counts)
    orders_by_status: Dict[str, int] = {}
    for status in OrderStatus:
        count = (
            db.query(func.count(Order.id))
            .filter(Order.status == status)
            .scalar()
            or 0
        )
        orders_by_status[status.value] = count

    # Revenue today: sum of order totals for payments approved today
    # Payments approved today -> get their order totals
    revenue_today = (
        db.query(func.coalesce(func.sum(Order.total), 0))
        .join(Payment, Order.id == Payment.order_id)
        .filter(Payment.status == PaymentStatus.APPROVED)
        .filter(func.date(Payment.reviewed_at) == today)
        .scalar()
        or Decimal("0.00")
    )

    # Recent orders (last 10)
    recent_orders = (
        db.query(Order)
        .order_by(Order.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "orders_today": orders_today,
        "pending_payments_count": pending_payments_count,
        "orders_by_status": orders_by_status,
        "revenue_today": float(revenue_today),
        "recent_orders": recent_orders,
    }

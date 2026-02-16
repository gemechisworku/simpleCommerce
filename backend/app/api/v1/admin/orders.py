"""
Admin order management endpoints
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import require_sales_or_admin
from app.models.user import User
from app.models.order import OrderStatus
from app.schemas.order import OrderResponse, OrderListItemResponse, OrderStatusUpdateRequest, OrderCancelRequest
from app.schemas.common import ResponseModel, PaginatedResponse, PaginationMeta
from app.services.order import get_order_by_id, list_all_orders, update_order_status, cancel_order
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OrderListItemResponse], status_code=status.HTTP_200_OK)
async def list_all_orders_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    order_number: Optional[str] = Query(None, description="Filter by order number"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    List all orders with filters
    
    Requires sales or admin role.
    """
    skip = (page - 1) * per_page
    order_status = None
    if status_filter:
        try:
            order_status = OrderStatus(status_filter)
        except ValueError:
            pass
    
    orders, total = list_all_orders(
        db=db,
        skip=skip,
        limit=per_page,
        status=order_status,
        user_id=user_id,
        order_number=order_number,
        date_from=date_from,
        date_to=date_to
    )
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        data=[OrderListItemResponse.model_validate(o) for o in orders],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )


@router.get("/{order_id}", response_model=ResponseModel[OrderResponse], status_code=status.HTTP_200_OK)
async def get_order_endpoint(
    order_id: int,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get order detail by ID (any order)
    
    Requires sales or admin role.
    """
    order = get_order_by_id(db, order_id)
    
    if not order:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"Order with id {order_id} not found")
    
    return ResponseModel(data=OrderResponse.model_validate(order))


@router.patch("/{order_id}/status", response_model=ResponseModel[OrderResponse], status_code=status.HTTP_200_OK)
async def update_order_status_endpoint(
    order_id: int,
    status_data: OrderStatusUpdateRequest,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    Update order status
    
    Requires sales or admin role.
    """
    try:
        new_status = OrderStatus(status_data.status)
    except ValueError:
        from app.core.exceptions import BusinessRuleError
        raise BusinessRuleError(f"Invalid order status: {status_data.status}")
    
    order = update_order_status(db, order_id, new_status, current_user.id, status_data.note)
    return ResponseModel(data=OrderResponse.model_validate(order))


@router.post("/{order_id}/cancel", response_model=ResponseModel[OrderResponse], status_code=status.HTTP_200_OK)
async def cancel_order_endpoint(
    order_id: int,
    cancel_data: OrderCancelRequest,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    Cancel order (admin/sales)
    
    Requires sales or admin role.
    Can cancel any order (except DELIVERED).
    """
    # For admin cancellation, we need to modify the cancel_order function or create a new one
    # For now, using the same function but with admin override
    order = get_order_by_id(db, order_id)
    if not order:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"Order with id {order_id} not found")
    
    if order.status == OrderStatus.DELIVERED:
        from app.core.exceptions import BusinessRuleError
        raise BusinessRuleError("Cannot cancel a delivered order")
    
    # Use cancel_order but we'll need to modify it to support admin cancellation
    # For now, let's use update_order_status to CANCELLED
    from app.models.order import OrderStatus
    order = update_order_status(db, order_id, OrderStatus.CANCELLED, current_user.id, cancel_data.reason or "Cancelled by admin")
    
    return ResponseModel(data=OrderResponse.model_validate(order))


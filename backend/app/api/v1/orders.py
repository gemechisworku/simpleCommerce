"""
Customer order endpoints
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.order import OrderStatus
from app.schemas.order import OrderCreate, OrderResponse, OrderListItemResponse, OrderCancelRequest
from app.schemas.common import ResponseModel, PaginatedResponse, PaginationMeta
from app.schemas.payment import PaymentMethodResponse
from app.services.order import create_order, get_order_by_id, list_user_orders, cancel_order
from app.services.payment import list_payment_methods
from app.core.config import settings

router = APIRouter()


@router.post("/checkout", response_model=ResponseModel[OrderResponse], status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create order from cart items
    
    Requires authentication.
    """
    order = create_order(db, current_user.id, order_data)
    return ResponseModel(data=OrderResponse.model_validate(order))


@router.get("/my", response_model=PaginatedResponse[OrderListItemResponse], status_code=status.HTTP_200_OK)
async def list_my_orders(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List current user's orders
    
    Requires authentication.
    """
    skip = (page - 1) * per_page
    order_status = None
    if status_filter:
        try:
            order_status = OrderStatus(status_filter)
        except ValueError:
            pass
    
    orders, total = list_user_orders(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=per_page,
        status=order_status
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


@router.get("/my/{order_id}", response_model=ResponseModel[OrderResponse], status_code=status.HTTP_200_OK)
async def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order detail by ID (own orders only)
    
    Requires authentication.
    """
    order = get_order_by_id(db, order_id)
    
    if not order:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"Order with id {order_id} not found")
    
    # Verify ownership
    if order.user_id != current_user.id:
        from app.core.exceptions import AuthorizationError
        raise AuthorizationError("You can only view your own orders")
    
    return ResponseModel(data=OrderResponse.model_validate(order))


@router.post("/my/{order_id}/cancel", response_model=ResponseModel[OrderResponse], status_code=status.HTTP_200_OK)
async def cancel_my_order(
    order_id: int,
    cancel_data: OrderCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel order (own orders only)
    
    Requires authentication.
    Only orders with status PENDING_PAYMENT can be cancelled.
    """
    order = cancel_order(db, order_id, current_user.id, cancel_data.reason)
    return ResponseModel(data=OrderResponse.model_validate(order))


@router.get("/payment-methods", response_model=ResponseModel[List[PaymentMethodResponse]], status_code=status.HTTP_200_OK)
async def list_payment_methods_public(
    db: Session = Depends(get_db)
):
    """
    List active payment methods (public endpoint)
    
    No authentication required.
    """
    payment_methods = list_payment_methods(db, active_only=True)
    return ResponseModel(data=[PaymentMethodResponse.model_validate(pm) for pm in payment_methods])


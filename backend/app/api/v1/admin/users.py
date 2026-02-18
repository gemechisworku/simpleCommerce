"""
Admin user management endpoints
"""
from fastapi import APIRouter, Depends, Query, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User, UserRole
from app.models.order import Order
from app.schemas.user import (
    UserResponse,
    UserListItemResponse,
    UserDetailResponse,
    AdminUserCreate,
    AdminUserRoleUpdate,
)
from app.schemas.common import ResponseModel, PaginatedResponse, PaginationMeta
from app.services.user import list_users, get_user_by_id, create_admin_user, update_user_role
from app.core.exceptions import NotFoundError

router = APIRouter()


def get_client_ip_from_request(request: Request) -> Optional[str]:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.get("", response_model=PaginatedResponse[UserListItemResponse], status_code=status.HTTP_200_OK)
async def list_users_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[str] = Query(None, description="Filter by role"),
    search: Optional[str] = Query(None, description="Search in name, phone, email"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with filters

    Requires admin role.
    """
    user_role = None
    if role:
        try:
            user_role = UserRole(role)
        except ValueError:
            pass

    skip = (page - 1) * per_page
    users, total = list_users(
        db=db,
        skip=skip,
        limit=per_page,
        role=user_role,
        search=search
    )

    total_pages = (total + per_page - 1) // per_page

    return PaginatedResponse(
        data=[UserListItemResponse.model_validate(u) for u in users],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )


@router.get("/{user_id}", response_model=ResponseModel[UserDetailResponse], status_code=status.HTTP_200_OK)
async def get_user_endpoint(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get user detail with orders count and recent orders

    Requires admin role.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(f"User with id {user_id} not found")

    # Get orders count
    orders_count = db.query(Order).filter(Order.user_id == user_id).count()

    # Get recent order IDs (last 5)
    recent_orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )
    recent_order_ids = [o.id for o in recent_orders]

    return ResponseModel(
        data=UserDetailResponse(
            id=user.id,
            phone=user.phone,
            phone_verified=user.phone_verified,
            email=user.email,
            email_verified=user.email_verified,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            orders_count=orders_count,
            recent_order_ids=recent_order_ids,
        )
    )


@router.post("", response_model=ResponseModel[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_data: AdminUserCreate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create new Sales or Admin user

    Sends OTP to phone for initial verification.
    Requires admin role.
    """
    try:
        role = UserRole(user_data.role)
    except ValueError:
        from app.core.exceptions import BusinessRuleError
        raise BusinessRuleError(f"Invalid role: {user_data.role}. Must be 'sales' or 'admin'")

    ip_address = get_client_ip_from_request(request)
    user = create_admin_user(
        db=db,
        phone=user_data.phone,
        role=role,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        ip_address=ip_address,
    )

    return ResponseModel(data=UserResponse.model_validate(user))


@router.patch("/{user_id}/role", response_model=ResponseModel[UserResponse], status_code=status.HTTP_200_OK)
async def update_user_role_endpoint(
    user_id: UUID,
    role_data: AdminUserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user role

    Cannot change own role. Cannot remove last admin.
    Requires admin role.
    """
    try:
        new_role = UserRole(role_data.role)
    except ValueError:
        from app.core.exceptions import BusinessRuleError
        raise BusinessRuleError(f"Invalid role: {role_data.role}")

    user = update_user_role(
        db=db,
        user_id=user_id,
        new_role=new_role,
        current_user_id=current_user.id,
    )

    return ResponseModel(data=UserResponse.model_validate(user))

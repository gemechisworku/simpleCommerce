"""
Admin payment method management endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.models.payment import PaymentMethodType
from app.schemas.payment import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse
)
from app.schemas.common import ResponseModel
from app.services.payment import create_payment_method, list_payment_methods
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.post("", response_model=ResponseModel[PaymentMethodResponse], status_code=status.HTTP_201_CREATED)
async def create_payment_method_endpoint(
    method_data: PaymentMethodCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create payment method
    
    Requires admin role.
    """
    try:
        method_type = PaymentMethodType(method_data.type)
    except ValueError:
        from app.core.exceptions import BusinessRuleError
        raise BusinessRuleError(f"Invalid payment method type: {method_data.type}")
    
    method = create_payment_method(
        db=db,
        type=method_type,
        name=method_data.name,
        account_identifier=method_data.account_identifier,
        account_holder=method_data.account_holder,
        instructions=method_data.instructions,
        is_active=method_data.is_active,
        sort_order=method_data.sort_order
    )
    
    return ResponseModel(data=PaymentMethodResponse.model_validate(method))


@router.get("", response_model=ResponseModel[list[PaymentMethodResponse]], status_code=status.HTTP_200_OK)
async def list_payment_methods_endpoint(
    active_only: bool = True,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List payment methods
    
    Requires admin role.
    """
    methods = list_payment_methods(db, active_only=active_only)
    return ResponseModel(data=[PaymentMethodResponse.model_validate(m) for m in methods])


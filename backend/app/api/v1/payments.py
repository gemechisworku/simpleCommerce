"""
Payment endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from uuid import UUID
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_sales_or_admin
from app.models.user import User
from app.schemas.payment import (
    PaymentSubmitRequest,
    PaymentResponse,
    PaymentReviewRequest,
    PaymentRejectRequest
)
from app.schemas.common import ResponseModel, PaginatedResponse, PaginationMeta
from app.services.payment import (
    submit_payment,
    list_payment_queue,
    approve_payment,
    reject_payment,
    request_payment_resubmission
)
from app.core.storage import minio_client
from app.core.config import settings
from app.core.exceptions import BusinessRuleError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/submit", response_model=ResponseModel[PaymentResponse], status_code=status.HTTP_201_CREATED)
async def submit_payment_endpoint(
    order_id: int = Query(..., description="Order ID"),
    method_id: int = Query(..., description="Payment method ID"),
    amount_declared: Optional[float] = Query(None, description="Declared payment amount"),
    reference_text: Optional[str] = Query(None, description="Payment reference"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit payment screenshot for an order
    
    Requires authentication.
    Validates file type (jpg/png) and size (max 5MB).
    """
    # Validate file type
    content_type = file.content_type
    if content_type not in settings.ALLOWED_FILE_TYPES.split(","):
        raise BusinessRuleError(f"Invalid file type. Allowed types: {settings.ALLOWED_FILE_TYPES}")
    
    # Validate file size (5MB max)
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise BusinessRuleError(f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB")
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"payments/{order_id}/{uuid.uuid4()}.{file_extension}"
    
    # Upload to MinIO
    try:
        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=filename,
            data=file_content,
            length=len(file_content),
            content_type=content_type
        )
        
        # Generate URL
        screenshot_url = f"/storage/{settings.MINIO_BUCKET_NAME}/{filename}"
        
        # Submit payment
        from decimal import Decimal
        payment = submit_payment(
            db=db,
            user_id=current_user.id,
            order_id=order_id,
            method_id=method_id,
            screenshot_url=screenshot_url,
            amount_declared=Decimal(str(amount_declared)) if amount_declared else None,
            reference_text=reference_text
        )
        
        return ResponseModel(data=PaymentResponse.model_validate(payment))
        
    except Exception as e:
        logger.error(f"Error submitting payment: {str(e)}")
        raise BusinessRuleError(f"Failed to submit payment: {str(e)}")


@router.get("/queue", response_model=PaginatedResponse[PaymentResponse], status_code=status.HTTP_200_OK)
async def list_payment_queue_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    method_id: Optional[int] = Query(None, description="Filter by payment method"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    List payments in review queue (submitted status)
    
    Requires sales or admin role.
    """
    skip = (page - 1) * per_page
    payments, total = list_payment_queue(
        db=db,
        skip=skip,
        limit=per_page,
        date_from=date_from,
        date_to=date_to,
        method_id=method_id,
        user_id=user_id
    )
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        data=[PaymentResponse.model_validate(p) for p in payments],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )


@router.get("/queue/{payment_id}", response_model=ResponseModel[PaymentResponse], status_code=status.HTTP_200_OK)
async def get_payment_detail(
    payment_id: int,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get payment detail from queue
    
    Requires sales or admin role.
    """
    from app.models.payment import Payment
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"Payment with id {payment_id} not found")
    
    return ResponseModel(data=PaymentResponse.model_validate(payment))


@router.post("/queue/{payment_id}/approve", response_model=ResponseModel[PaymentResponse], status_code=status.HTTP_200_OK)
async def approve_payment_endpoint(
    payment_id: int,
    review_data: PaymentReviewRequest,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    Approve payment
    
    Requires sales or admin role.
    """
    payment = approve_payment(db, payment_id, current_user.id, review_data.note)
    return ResponseModel(data=PaymentResponse.model_validate(payment))


@router.post("/queue/{payment_id}/reject", response_model=ResponseModel[PaymentResponse], status_code=status.HTTP_200_OK)
async def reject_payment_endpoint(
    payment_id: int,
    reject_data: PaymentRejectRequest,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    Reject payment
    
    Requires sales or admin role.
    """
    payment = reject_payment(db, payment_id, current_user.id, reject_data.reason)
    return ResponseModel(data=PaymentResponse.model_validate(payment))


@router.post("/queue/{payment_id}/request-resubmission", response_model=ResponseModel[PaymentResponse], status_code=status.HTTP_200_OK)
async def request_payment_resubmission_endpoint(
    payment_id: int,
    review_data: PaymentReviewRequest,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """
    Request payment resubmission
    
    Requires sales or admin role.
    """
    payment = request_payment_resubmission(db, payment_id, current_user.id, review_data.note)
    return ResponseModel(data=PaymentResponse.model_validate(payment))


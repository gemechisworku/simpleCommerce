"""
Payment service for managing payments
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from decimal import Decimal
from datetime import datetime, timezone, date
from uuid import UUID

from app.models.payment import Payment, PaymentMethod, PaymentStatus, PaymentMethodType
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.models.notification import NotificationType
from app.core.exceptions import NotFoundError, BusinessRuleError
from app.schemas.payment import PaymentSubmitRequest
from app.services.notification import create_notification
from app.services.user.user_service import get_user_ids_by_roles
import logging

logger = logging.getLogger(__name__)


def create_payment_method(
    db: Session,
    type: PaymentMethodType,
    name: str,
    account_identifier: str,
    account_holder: str,
    instructions: Optional[str] = None,
    is_active: bool = True,
    sort_order: int = 0
) -> PaymentMethod:
    """Create payment method"""
    payment_method = PaymentMethod(
        type=type,
        name=name,
        account_identifier=account_identifier,
        account_holder=account_holder,
        instructions=instructions,
        is_active=is_active,
        sort_order=sort_order
    )
    
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    
    logger.info(f"Created payment method: {name} (id: {payment_method.id})")
    return payment_method


def list_payment_methods(db: Session, active_only: bool = True) -> List[PaymentMethod]:
    """List payment methods"""
    query = db.query(PaymentMethod)
    
    if active_only:
        query = query.filter(PaymentMethod.is_active == True)
    
    return query.order_by(PaymentMethod.sort_order.asc()).all()


def get_payment_method_by_id(db: Session, method_id: int) -> Optional[PaymentMethod]:
    """Get payment method by ID"""
    return db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()


def update_payment_method(
    db: Session,
    method_id: int,
    name: Optional[str] = None,
    account_identifier: Optional[str] = None,
    account_holder: Optional[str] = None,
    instructions: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_order: Optional[int] = None
) -> PaymentMethod:
    """Update payment method. Only provided fields are updated."""
    method = get_payment_method_by_id(db, method_id)
    if not method:
        raise NotFoundError(f"Payment method with id {method_id} not found")
    if name is not None:
        method.name = name
    if account_identifier is not None:
        method.account_identifier = account_identifier
    if account_holder is not None:
        method.account_holder = account_holder
    if instructions is not None:
        method.instructions = instructions
    if is_active is not None:
        method.is_active = is_active
    if sort_order is not None:
        method.sort_order = sort_order
    db.commit()
    db.refresh(method)
    logger.info(f"Updated payment method id {method_id}")
    return method


def submit_payment(
    db: Session,
    user_id: UUID,
    order_id: int,
    method_id: int,
    screenshot_url: str,
    amount_declared: Optional[Decimal] = None,
    reference_text: Optional[str] = None,
    paid_at: Optional[datetime] = None
) -> Payment:
    """
    Submit payment for an order
    
    Args:
        db: Database session
        user_id: User ID submitting payment
        order_id: Order ID
        method_id: Payment method ID
        screenshot_url: URL of payment screenshot
        amount_declared: Declared payment amount
        reference_text: Payment reference/transaction ID
        paid_at: Payment date/time
        
    Returns:
        Created Payment object
        
    Raises:
        NotFoundError: If order or payment method not found
        BusinessRuleError: If order status doesn't allow payment submission
    """
    # Validate order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise NotFoundError(f"Order with id {order_id} not found")
    
    # Verify ownership
    if order.user_id != user_id:
        raise BusinessRuleError("You can only submit payment for your own orders")
    
    # Validate order status
    if order.status not in [OrderStatus.PENDING_PAYMENT, OrderStatus.PAYMENT_REJECTED, OrderStatus.PAYMENT_RESUBMIT_REQUESTED]:
        raise BusinessRuleError(f"Payment cannot be submitted for order with status '{order.status.value}'")
    
    # Validate payment method
    payment_method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == method_id,
            PaymentMethod.is_active == True
        )
    ).first()
    
    if not payment_method:
        raise NotFoundError(f"Active payment method with id {method_id} not found")
    
    # Create payment
    payment = Payment(
        order_id=order_id,
        method_id=method_id,
        submitted_by_user_id=user_id,
        amount_declared=amount_declared,
        reference_text=reference_text,
        paid_at=paid_at or datetime.now(timezone.utc),
        screenshot_url=screenshot_url,
        status=PaymentStatus.SUBMITTED
    )
    
    db.add(payment)
    
    # Update order status
    order.status = OrderStatus.PAYMENT_SUBMITTED
    
    # Create status history
    from app.models.order import OrderStatusHistory
    status_history = OrderStatusHistory(
        order_id=order.id,
        old_status=OrderStatus.PENDING_PAYMENT,
        new_status=OrderStatus.PAYMENT_SUBMITTED,
        actor_user_id=user_id,
        note="Payment submitted"
    )
    db.add(status_history)
    
    db.commit()
    db.refresh(payment)
    
    # Notify sales/admin users of new payment submission
    for uid in get_user_ids_by_roles(db, [UserRole.SALES, UserRole.ADMIN]):
        create_notification(
            db, uid, NotificationType.NEW_PAYMENT_SUBMITTED,
            "New payment submitted",
            f"Payment submitted for order {order.order_number}. Please review."
        )
    
    logger.info(f"Submitted payment for order {order.order_number} (payment id: {payment.id})")
    return payment


def list_payment_queue(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    method_id: Optional[int] = None,
    user_id: Optional[UUID] = None
) -> Tuple[List[Payment], int]:
    """
    List payments in review queue (submitted status)
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        date_from: Filter payments from date
        date_to: Filter payments to date
        method_id: Filter by payment method
        user_id: Filter by user ID
        
    Returns:
        Tuple of (payments list, total count)
    """
    query = db.query(Payment).filter(Payment.status == PaymentStatus.SUBMITTED)
    
    if date_from:
        query = query.filter(func.date(Payment.created_at) >= date_from)
    
    if date_to:
        query = query.filter(func.date(Payment.created_at) <= date_to)
    
    if method_id:
        query = query.filter(Payment.method_id == method_id)
    
    if user_id:
        query = query.filter(Payment.submitted_by_user_id == user_id)
    
    total = query.count()
    payments = query.order_by(Payment.created_at.asc()).offset(skip).limit(limit).all()
    
    return payments, total


def approve_payment(
    db: Session,
    payment_id: int,
    reviewer_user_id: UUID,
    note: Optional[str] = None
) -> Payment:
    """
    Approve payment
    
    Args:
        db: Database session
        payment_id: Payment ID
        reviewer_user_id: User ID approving payment
        note: Review note
        
    Returns:
        Approved Payment object
        
    Raises:
        NotFoundError: If payment not found
        BusinessRuleError: If payment status is not submitted
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise NotFoundError(f"Payment with id {payment_id} not found")
    
    if payment.status != PaymentStatus.SUBMITTED:
        raise BusinessRuleError(f"Payment with status '{payment.status.value}' cannot be approved")
    
    # Update payment
    payment.status = PaymentStatus.APPROVED
    payment.reviewed_by = reviewer_user_id
    payment.reviewed_at = datetime.now(timezone.utc)
    payment.review_note = note
    
    # Update order status
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order:
        old_status = order.status
        order.status = OrderStatus.PAID
        
        # Create status history
        from app.models.order import OrderStatusHistory
        status_history = OrderStatusHistory(
            order_id=order.id,
            old_status=old_status,
            new_status=OrderStatus.PAID,
            actor_user_id=reviewer_user_id,
            note=note or "Payment approved"
        )
        db.add(status_history)
    
    db.commit()
    db.refresh(payment)
    
    # Notify customer
    if order and order.user_id:
        create_notification(
            db, order.user_id, NotificationType.PAYMENT_APPROVED,
            "Payment approved",
            f"Your payment for order {order.order_number} has been approved."
        )
    
    logger.info(f"Approved payment {payment_id} for order {order.order_number if order else 'N/A'}")
    return payment


def reject_payment(
    db: Session,
    payment_id: int,
    reviewer_user_id: UUID,
    reason: str
) -> Payment:
    """
    Reject payment
    
    Args:
        db: Database session
        payment_id: Payment ID
        reviewer_user_id: User ID rejecting payment
        reason: Rejection reason
        
    Returns:
        Rejected Payment object
        
    Raises:
        NotFoundError: If payment not found
        BusinessRuleError: If payment status is not submitted
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise NotFoundError(f"Payment with id {payment_id} not found")
    
    if payment.status != PaymentStatus.SUBMITTED:
        raise BusinessRuleError(f"Payment with status '{payment.status.value}' cannot be rejected")
    
    # Update payment
    payment.status = PaymentStatus.REJECTED
    payment.reviewed_by = reviewer_user_id
    payment.reviewed_at = datetime.now(timezone.utc)
    payment.review_note = reason
    
    # Update order status
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order:
        old_status = order.status
        order.status = OrderStatus.PAYMENT_REJECTED
        
        # Create status history
        from app.models.order import OrderStatusHistory
        status_history = OrderStatusHistory(
            order_id=order.id,
            old_status=old_status,
            new_status=OrderStatus.PAYMENT_REJECTED,
            actor_user_id=reviewer_user_id,
            note=f"Payment rejected: {reason}"
        )
        db.add(status_history)
    
    db.commit()
    db.refresh(payment)
    
    # Notify customer
    if order and order.user_id:
        create_notification(
            db, order.user_id, NotificationType.PAYMENT_REJECTED,
            "Payment rejected",
            f"Your payment for order {order.order_number} was rejected. Reason: {reason}"
        )
    
    logger.info(f"Rejected payment {payment_id} for order {order.order_number if order else 'N/A'}")
    return payment


def request_payment_resubmission(
    db: Session,
    payment_id: int,
    reviewer_user_id: UUID,
    note: Optional[str] = None
) -> Payment:
    """
    Request payment resubmission
    
    Args:
        db: Database session
        payment_id: Payment ID
        reviewer_user_id: User ID requesting resubmission
        note: Request note
        
    Returns:
        Updated Payment object
        
    Raises:
        NotFoundError: If payment not found
        BusinessRuleError: If payment status is not submitted
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise NotFoundError(f"Payment with id {payment_id} not found")
    
    if payment.status != PaymentStatus.SUBMITTED:
        raise BusinessRuleError(f"Payment with status '{payment.status.value}' cannot be requested for resubmission")
    
    # Update payment
    payment.status = PaymentStatus.RESUBMIT_REQUESTED
    payment.reviewed_by = reviewer_user_id
    payment.reviewed_at = datetime.now(timezone.utc)
    payment.review_note = note
    
    # Update order status
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order:
        old_status = order.status
        order.status = OrderStatus.PAYMENT_RESUBMIT_REQUESTED
        
        # Create status history
        from app.models.order import OrderStatusHistory
        status_history = OrderStatusHistory(
            order_id=order.id,
            old_status=old_status,
            new_status=OrderStatus.PAYMENT_RESUBMIT_REQUESTED,
            actor_user_id=reviewer_user_id,
            note=note or "Payment resubmission requested"
        )
        db.add(status_history)
    
    db.commit()
    db.refresh(payment)
    
    # Notify customer
    if order and order.user_id:
        create_notification(
            db, order.user_id, NotificationType.PAYMENT_RESUBMIT_REQUESTED,
            "Payment resubmission requested",
            f"Please resubmit your payment for order {order.order_number}." + (f" Note: {note}" if note else "")
        )
    
    logger.info(f"Requested resubmission for payment {payment_id} for order {order.order_number if order else 'N/A'}")
    return payment


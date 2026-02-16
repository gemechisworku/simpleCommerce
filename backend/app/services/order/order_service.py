"""
Order service for managing orders
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from decimal import Decimal
from datetime import datetime, timezone, date, timedelta
from uuid import UUID

from app.models.order import Order, OrderItem, OrderStatus, OrderStatusHistory
from app.models.product import Product, ProductVariant
from app.models.delivery_zone import DeliveryZone
from app.models.user import User
from app.core.exceptions import NotFoundError, BusinessRuleError, ConflictError
from app.utils.helpers import generate_order_number, calculate_delivery_dates
from app.schemas.order import OrderCreate, OrderItemCreate
import logging

logger = logging.getLogger(__name__)


def create_order(db: Session, user_id: UUID, order_data: OrderCreate) -> Order:
    """
    Create a new order
    
    Args:
        db: Database session
        user_id: User ID creating the order
        order_data: Order creation data
        
    Returns:
        Created Order object
        
    Raises:
        NotFoundError: If delivery zone, product, or variant not found
        BusinessRuleError: If stock insufficient or validation fails
    """
    # Validate delivery zone
    delivery_zone = db.query(DeliveryZone).filter(
        and_(
            DeliveryZone.id == order_data.delivery_zone_id,
            DeliveryZone.is_active == True
        )
    ).first()
    
    if not delivery_zone:
        raise NotFoundError(f"Active delivery zone with id {order_data.delivery_zone_id} not found")
    
    # Validate and process items
    order_items = []
    subtotal = Decimal("0.00")
    
    for item_data in order_data.items:
        # Get variant
        variant = db.query(ProductVariant).filter(
            and_(
                ProductVariant.id == item_data.variant_id,
                ProductVariant.is_active == True
            )
        ).first()
        
        if not variant:
            raise NotFoundError(f"Active variant with id {item_data.variant_id} not found")
        
        # Check stock
        if variant.stock_qty < item_data.quantity:
            raise BusinessRuleError(
                f"Insufficient stock for variant '{variant.label}'. Available: {variant.stock_qty}, Requested: {item_data.quantity}"
            )
        
        # Get product for snapshot
        product = db.query(Product).filter(Product.id == variant.product_id).first()
        if not product or product.deleted_at is not None or not product.is_active:
            raise NotFoundError(f"Active product for variant {item_data.variant_id} not found")
        
        # Calculate line total
        unit_price = variant.price
        line_total = unit_price * item_data.quantity
        subtotal += line_total
        
        # Create order item (with snapshots)
        order_item = OrderItem(
            product_id=product.id,
            variant_id=variant.id,
            product_name=product.name,
            variant_label=variant.label,
            quantity=item_data.quantity,
            unit_price=unit_price,
            line_total=line_total
        )
        order_items.append(order_item)
        
        # Reserve stock (decrement)
        variant.stock_qty -= item_data.quantity
    
    # Calculate delivery fee and total
    delivery_fee = delivery_zone.fee
    total = subtotal + delivery_fee
    
    # Calculate expected delivery dates
    expected_from, expected_to = calculate_delivery_dates(
        delivery_zone.eta_min_days,
        delivery_zone.eta_max_days
    )
    
    # Generate unique order number
    order_number = generate_order_number()
    
    # Ensure order number is unique
    while db.query(Order).filter(Order.order_number == order_number).first():
        order_number = generate_order_number()
    
    # Create order
    order = Order(
        order_number=order_number,
        user_id=user_id,
        status=OrderStatus.PENDING_PAYMENT,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        delivery_zone_id=delivery_zone.id,
        delivery_address=order_data.delivery_address,
        recipient_name=order_data.recipient_name,
        recipient_phone=order_data.recipient_phone,
        delivery_instructions=order_data.delivery_instructions,
        expected_delivery_from=expected_from,
        expected_delivery_to=expected_to
    )
    
    db.add(order)
    db.flush()  # Get order.id
    
    # Add order items
    for item in order_items:
        item.order_id = order.id
        db.add(item)
    
    # Create initial status history
    status_history = OrderStatusHistory(
        order_id=order.id,
        old_status=None,
        new_status=OrderStatus.PENDING_PAYMENT,
        actor_user_id=user_id,
        note="Order created"
    )
    db.add(status_history)
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"Created order: {order.order_number} (id: {order.id})")
    return order


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
    """Get order by order number"""
    return db.query(Order).filter(Order.order_number == order_number).first()


def list_user_orders(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 10,
    status: Optional[OrderStatus] = None
) -> Tuple[List[Order], int]:
    """
    List orders for a user
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status
        
    Returns:
        Tuple of (orders list, total count)
    """
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return orders, total


def list_all_orders(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: Optional[OrderStatus] = None,
    user_id: Optional[UUID] = None,
    order_number: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> Tuple[List[Order], int]:
    """
    List all orders (admin/sales)
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status
        user_id: Filter by user ID
        order_number: Filter by order number (partial match)
        date_from: Filter orders from date
        date_to: Filter orders to date
        
    Returns:
        Tuple of (orders list, total count)
    """
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if order_number:
        query = query.filter(Order.order_number.ilike(f"%{order_number}%"))
    
    if date_from:
        query = query.filter(func.date(Order.created_at) >= date_from)
    
    if date_to:
        query = query.filter(func.date(Order.created_at) <= date_to)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return orders, total


def cancel_order(db: Session, order_id: int, user_id: UUID, reason: Optional[str] = None) -> Order:
    """
    Cancel order (customer)
    
    Args:
        db: Database session
        order_id: Order ID
        user_id: User ID (must own the order)
        reason: Cancellation reason
        
    Returns:
        Cancelled Order object
        
    Raises:
        NotFoundError: If order not found
        BusinessRuleError: If order cannot be cancelled
    """
    order = get_order_by_id(db, order_id)
    
    if not order:
        raise NotFoundError(f"Order with id {order_id} not found")
    
    # Verify ownership
    if order.user_id != user_id:
        raise BusinessRuleError("You can only cancel your own orders")
    
    # Validate status
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise BusinessRuleError(f"Order with status '{order.status.value}' cannot be cancelled")
    
    # Check if payment approved
    from app.models.payment import Payment, PaymentStatus
    approved_payment = db.query(Payment).filter(
        and_(
            Payment.order_id == order_id,
            Payment.status == PaymentStatus.APPROVED
        )
    ).first()
    
    if approved_payment:
        raise BusinessRuleError("Cannot cancel order with approved payment")
    
    # Update order
    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.now(timezone.utc)
    order.cancellation_reason = reason
    
    # Create status history
    status_history = OrderStatusHistory(
        order_id=order.id,
        old_status=OrderStatus.PENDING_PAYMENT,
        new_status=OrderStatus.CANCELLED,
        actor_user_id=user_id,
        note=reason or "Order cancelled by customer"
    )
    db.add(status_history)
    
    # Release stock (increment stock_qty)
    for item in order.items:
        if item.variant_id:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
            if variant:
                variant.stock_qty += item.quantity
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"Cancelled order: {order.order_number} (id: {order.id})")
    return order


def update_order_status(
    db: Session,
    order_id: int,
    new_status: OrderStatus,
    actor_user_id: UUID,
    note: Optional[str] = None
) -> Order:
    """
    Update order status (admin/sales)
    
    Args:
        db: Database session
        order_id: Order ID
        new_status: New order status
        actor_user_id: User ID performing the action
        note: Status change note
        
    Returns:
        Updated Order object
        
    Raises:
        NotFoundError: If order not found
        BusinessRuleError: If status transition is invalid
    """
    order = get_order_by_id(db, order_id)
    
    if not order:
        raise NotFoundError(f"Order with id {order_id} not found")
    
    old_status = order.status
    
    # Validate status transition
    valid_transitions = {
        OrderStatus.PAID: [OrderStatus.PACKING],
        OrderStatus.PACKING: [OrderStatus.DISPATCHED],
        OrderStatus.DISPATCHED: [OrderStatus.DELIVERED],
    }
    
    if old_status in valid_transitions:
        if new_status not in valid_transitions[old_status]:
            raise BusinessRuleError(
                f"Invalid status transition from '{old_status.value}' to '{new_status.value}'"
            )
    
    # Update order
    order.status = new_status
    
    # Create status history
    status_history = OrderStatusHistory(
        order_id=order.id,
        old_status=old_status,
        new_status=new_status,
        actor_user_id=actor_user_id,
        note=note
    )
    db.add(status_history)
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"Updated order {order.order_number} status: {old_status.value} -> {new_status.value}")
    return order


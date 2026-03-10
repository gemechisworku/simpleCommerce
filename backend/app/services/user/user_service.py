"""
User service for admin user management
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.user import User, UserRole
from app.models.auth import OTPCode, OTPType, OTPPurpose
from app.utils.helpers import validate_phone, validate_email
from app.core.exceptions import BusinessRuleError, NotFoundError, ConflictError
from app.services.auth.otp_service import create_otp
import logging

logger = logging.getLogger(__name__)


def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    role: Optional[UserRole] = None,
    search: Optional[str] = None
) -> Tuple[List[User], int]:
    """
    List users with filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        role: Filter by role
        search: Search in name, phone, email

    Returns:
        Tuple of (users list, total count)
    """
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.phone.ilike(search_term),
                User.email.ilike(search_term),
            )
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    return users, total


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_ids_by_roles(db: Session, roles: List[UserRole]) -> List[UUID]:
    """Get user IDs that have any of the given roles (active users only)."""
    if not roles:
        return []
    users = db.query(User).filter(User.role.in_(roles), User.is_active == True).all()
    return [u.id for u in users]


def create_admin_user(
    db: Session,
    phone: str,
    role: UserRole,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> User:
    """
    Create a new Sales or Admin user

    Args:
        db: Database session
        phone: Phone number (required)
        role: User role (sales or admin)
        email: Optional email
        first_name: Optional first name
        last_name: Optional last name
        ip_address: Client IP for OTP rate limiting

    Returns:
        Created User object

    Raises:
        BusinessRuleError: If validation fails
        ConflictError: If phone or email already exists
    """
    if role not in [UserRole.SALES, UserRole.ADMIN]:
        raise BusinessRuleError("Can only create Sales or Admin users")

    if not validate_phone(phone):
        raise BusinessRuleError("Invalid phone number format. Please use E.164 format (e.g., +251912345678)")

    if email and not validate_email(email):
        raise BusinessRuleError("Invalid email format")

    # Check phone uniqueness
    if db.query(User).filter(User.phone == phone).first():
        raise ConflictError(f"User with phone {phone} already exists")

    # Check email uniqueness if provided
    if email and db.query(User).filter(User.email == email).first():
        raise ConflictError(f"User with email {email} already exists")

    # Create user (phone_verified=False - they verify via OTP)
    user = User(
        phone=phone,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        phone_verified=False,
        email_verified=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send OTP for initial verification
    create_otp(
        db=db,
        identifier=phone,
        otp_type=OTPType.PHONE,
        purpose=OTPPurpose.LOGIN,
        ip_address=ip_address,
    )

    logger.info(f"Created {role.value} user: {phone} (id: {user.id})")
    return user


def update_user_role(
    db: Session,
    user_id: UUID,
    new_role: UserRole,
    current_user_id: UUID,
) -> User:
    """
    Update user role (admin only)

    Args:
        db: Database session
        user_id: User ID to update
        new_role: New role to assign
        current_user_id: ID of admin making the change

    Returns:
        Updated User object

    Raises:
        NotFoundError: If user not found
        BusinessRuleError: If cannot change own role or cannot remove last admin
    """
    if current_user_id == user_id:
        raise BusinessRuleError("Cannot change your own role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError(f"User with id {user_id} not found")

    # If demoting from admin, check we're not removing the last admin
    if user.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
        admin_count = db.query(func.count(User.id)).filter(User.role == UserRole.ADMIN).scalar() or 0
        if admin_count <= 1:
            raise BusinessRuleError("Cannot remove the last admin. Promote another user first.")

    user.role = new_role
    db.commit()
    db.refresh(user)

    logger.info(f"Updated user {user_id} role to {new_role.value} by {current_user_id}")
    return user

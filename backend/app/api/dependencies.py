"""
API dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User, UserRole
from typing import Optional

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User object
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    if not payload:
        raise AuthenticationError("Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (alias for get_current_user)
    """
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to require specific user roles
    
    Usage:
        @router.get("/admin")
        def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationError(f"Required role: {', '.join([r.value for r in allowed_roles])}")
        return current_user
    
    return role_checker


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if user.role != UserRole.ADMIN:
        raise AuthorizationError("Admin role required")
    return user


def require_sales_or_admin(user: User = Depends(get_current_user)) -> User:
    """Require sales or admin role"""
    if user.role not in [UserRole.SALES, UserRole.ADMIN]:
        raise AuthorizationError("Sales or Admin role required")
    return user


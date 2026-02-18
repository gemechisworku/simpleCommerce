"""
User service
"""
from app.services.user.user_service import (
    list_users,
    get_user_by_id,
    create_admin_user,
    update_user_role,
)

__all__ = [
    "list_users",
    "get_user_by_id",
    "create_admin_user",
    "update_user_role",
]

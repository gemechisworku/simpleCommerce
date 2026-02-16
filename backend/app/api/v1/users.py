"""
User profile endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import ConflictError
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import ResponseModel

router = APIRouter()


@router.get("/me", response_model=ResponseModel[UserResponse], status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile
    
    Requires authentication via Bearer token in Authorization header.
    
    Returns:
        User profile data including:
        - id, phone, email, telegram info
        - verification status
        - role and active status
        - name and timestamps
    """
    return ResponseModel(data=UserResponse.model_validate(current_user))


@router.patch("/me", response_model=ResponseModel[UserResponse], status_code=status.HTTP_200_OK)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    """
    # Update fields if provided
    if user_data.first_name is not None:
        current_user.first_name = user_data.first_name
    
    if user_data.last_name is not None:
        current_user.last_name = user_data.last_name
    
    if user_data.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise ConflictError("Email already registered to another account")
        
        current_user.email = user_data.email
        # Email verification will be handled separately via OTP
    
    db.commit()
    db.refresh(current_user)
    
    return ResponseModel(data=UserResponse.model_validate(current_user))


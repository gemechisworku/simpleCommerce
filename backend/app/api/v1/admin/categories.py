"""
Admin category management endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import ResponseModel
from app.services.category import (
    create_category,
    get_category_by_id,
    list_categories,
    update_category,
    delete_category,
)
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.post("", response_model=ResponseModel[CategoryResponse], status_code=status.HTTP_201_CREATED)
async def create_category_endpoint(
    category_data: CategoryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create category

    Requires admin role.
    """
    category = create_category(db, category_data)
    return ResponseModel(data=CategoryResponse.model_validate(category))


@router.get("", response_model=ResponseModel[list[CategoryResponse]], status_code=status.HTTP_200_OK)
async def list_categories_endpoint(
    active_only: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List categories

    Requires admin role.
    """
    categories = list_categories(db, active_only=active_only)
    return ResponseModel(data=[CategoryResponse.model_validate(c) for c in categories])


@router.get("/{category_id}", response_model=ResponseModel[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_category_endpoint(
    category_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get category by ID

    Requires admin role.
    """
    category = get_category_by_id(db, category_id)
    if not category:
        raise NotFoundError(f"Category with id {category_id} not found")
    return ResponseModel(data=CategoryResponse.model_validate(category))


@router.patch("/{category_id}", response_model=ResponseModel[CategoryResponse], status_code=status.HTTP_200_OK)
async def update_category_endpoint(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update category

    Requires admin role.
    """
    category = update_category(db, category_id, category_data)
    return ResponseModel(data=CategoryResponse.model_validate(category))


@router.delete("/{category_id}", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK)
async def delete_category_endpoint(
    category_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete category

    Requires admin role.
    """
    delete_category(db, category_id)
    return ResponseModel(data={"message": "Category deleted successfully"})

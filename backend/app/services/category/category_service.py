"""
Category service
"""
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.category import Category
from app.core.exceptions import NotFoundError, BusinessRuleError
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.utils.helpers import generate_slug
import logging

logger = logging.getLogger(__name__)


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    """Create category"""
    slug = generate_slug(category_data.name)
    existing = db.query(Category).filter(
        (Category.slug == slug) | (Category.name == category_data.name)
    ).first()
    if existing:
        raise BusinessRuleError(f"Category with name '{category_data.name}' already exists")

    category = Category(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        parent_id=category_data.parent_id,
        is_active=category_data.is_active,
        sort_order=category_data.sort_order,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    logger.info(f"Created category: {category.name} (id: {category.id})")
    return category


def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    """Get category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def list_categories(db: Session, active_only: bool = False) -> List[Category]:
    """List categories"""
    query = db.query(Category)
    if active_only:
        query = query.filter(Category.is_active == True)
    return query.order_by(Category.sort_order.asc(), Category.name.asc()).all()


def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Category:
    """Update category"""
    category = get_category_by_id(db, category_id)
    if not category:
        raise NotFoundError(f"Category with id {category_id} not found")

    if category_data.name is not None:
        slug = generate_slug(category_data.name)
        existing = db.query(Category).filter(
            Category.slug == slug,
            Category.id != category_id
        ).first()
        if existing:
            raise BusinessRuleError(f"Category with name '{category_data.name}' already exists")
        category.name = category_data.name
        category.slug = slug

    if category_data.description is not None:
        category.description = category_data.description
    if category_data.parent_id is not None:
        category.parent_id = category_data.parent_id
    if category_data.is_active is not None:
        category.is_active = category_data.is_active
    if category_data.sort_order is not None:
        category.sort_order = category_data.sort_order

    db.commit()
    db.refresh(category)
    logger.info(f"Updated category: {category.name} (id: {category.id})")
    return category


def delete_category(db: Session, category_id: int) -> None:
    """Delete category (products will have category_id set to NULL)"""
    category = get_category_by_id(db, category_id)
    if not category:
        raise NotFoundError(f"Category with id {category_id} not found")
    db.delete(category)
    db.commit()
    logger.info(f"Deleted category: {category.name} (id: {category.id})")

"""
Product service for managing products
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from decimal import Decimal
from datetime import datetime, timezone

from app.models.product import Product, ProductVariant, ProductImage
from app.models.category import Category
from app.core.exceptions import NotFoundError, ConflictError, BusinessRuleError
from app.utils.helpers import generate_slug
from app.schemas.product import ProductCreate, ProductUpdate, ProductVariantCreate
import logging

logger = logging.getLogger(__name__)


def create_product(db: Session, product_data: ProductCreate) -> Product:
    """
    Create a new product with variants
    
    Args:
        db: Database session
        product_data: Product creation data
        
    Returns:
        Created Product object
        
    Raises:
        NotFoundError: If category not found
        ConflictError: If slug already exists
    """
    # Validate category if provided
    if product_data.category_id:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise NotFoundError(f"Category with id {product_data.category_id} not found")
    
    # Generate slug from name
    base_slug = generate_slug(product_data.name)
    slug = base_slug
    counter = 1
    
    # Ensure slug is unique
    while db.query(Product).filter(Product.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Create product
    product = Product(
        name=product_data.name,
        slug=slug,
        description=product_data.description,
        category_id=product_data.category_id,
        is_active=product_data.is_active,
        is_featured=product_data.is_featured
    )
    
    db.add(product)
    db.flush()  # Flush to get product.id
    
    # Create variants if provided
    for variant_data in product_data.variants:
        variant = ProductVariant(
            product_id=product.id,
            label=variant_data.label,
            price=variant_data.price,
            stock_qty=variant_data.stock_qty,
            sku=variant_data.sku,
            is_active=variant_data.is_active
        )
        db.add(variant)
    
    db.commit()
    db.refresh(product)
    
    logger.info(f"Created product: {product.name} (id: {product.id})")
    return product


def get_product_by_id(db: Session, product_id: int, include_deleted: bool = False) -> Optional[Product]:
    """
    Get product by ID
    
    Args:
        db: Database session
        product_id: Product ID
        include_deleted: Whether to include soft-deleted products
        
    Returns:
        Product object or None
    """
    query = db.query(Product).filter(Product.id == product_id)
    
    if not include_deleted:
        query = query.filter(Product.deleted_at.is_(None))
    
    return query.first()


def get_product_by_slug(db: Session, slug: str, include_deleted: bool = False) -> Optional[Product]:
    """
    Get product by slug
    
    Args:
        db: Database session
        slug: Product slug
        include_deleted: Whether to include soft-deleted products
        
    Returns:
        Product object or None
    """
    query = db.query(Product).options(
        joinedload(Product.images),
        joinedload(Product.variants),
    ).filter(Product.slug == slug)

    if not include_deleted:
        query = query.filter(Product.deleted_at.is_(None))

    return query.first()


def list_products(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    include_deleted: bool = False
) -> Tuple[List[Product], int]:
    """
    List products with filters and pagination
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for name/description
        category_id: Filter by category
        is_active: Filter by active status
        is_featured: Filter by featured status
        include_deleted: Whether to include soft-deleted products
        
    Returns:
        Tuple of (products list, total count)
    """
    query = db.query(Product)
    
    # Exclude deleted products unless explicitly requested
    if not include_deleted:
        query = query.filter(Product.deleted_at.is_(None))
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    
    # Get total count
    total = query.count()
    
    # Eager-load images for list responses (e.g. admin list with image_url)
    query = query.options(joinedload(Product.images))
    # Apply pagination and ordering
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    
    return products, total


def list_public_products(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    is_featured: Optional[bool] = None
) -> Tuple[List[Product], int]:
    """
    List products for public browsing (only active, non-deleted products with active variants)
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for name/description
        category_id: Filter by category
        is_featured: Filter by featured status
        
    Returns:
        Tuple of (products list, total count)
    """
    # Get products with at least one active variant (eager load images)
    query = db.query(Product).options(
        joinedload(Product.images)
    ).join(ProductVariant).filter(
        and_(
            Product.deleted_at.is_(None),
            Product.is_active == True,
            ProductVariant.is_active == True
        )
    ).distinct()
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    products = query.order_by(
        Product.is_featured.desc(),
        Product.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return products, total


def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Product:
    """
    Update product
    
    Args:
        db: Database session
        product_id: Product ID
        product_data: Product update data
        
    Returns:
        Updated Product object
        
    Raises:
        NotFoundError: If product not found
        ConflictError: If new slug already exists
    """
    product = get_product_by_id(db, product_id, include_deleted=True)
    
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")
    
    # Update fields
    if product_data.name is not None:
        # Regenerate slug if name changed
        if product_data.name != product.name:
            base_slug = generate_slug(product_data.name)
            slug = base_slug
            counter = 1
            
            # Ensure slug is unique (excluding current product)
            while db.query(Product).filter(
                and_(Product.slug == slug, Product.id != product_id)
            ).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            product.name = product_data.name
            product.slug = slug
    
    if product_data.description is not None:
        product.description = product_data.description
    
    if product_data.category_id is not None:
        # Validate category
        if product_data.category_id:
            category = db.query(Category).filter(Category.id == product_data.category_id).first()
            if not category:
                raise NotFoundError(f"Category with id {product_data.category_id} not found")
        product.category_id = product_data.category_id
    
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    
    if product_data.is_featured is not None:
        product.is_featured = product_data.is_featured
    
    db.commit()
    db.refresh(product)
    
    logger.info(f"Updated product: {product.name} (id: {product.id})")
    return product


def delete_product(db: Session, product_id: int) -> Product:
    """
    Soft delete product
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        Deleted Product object
        
    Raises:
        NotFoundError: If product not found
    """
    product = get_product_by_id(db, product_id, include_deleted=True)
    
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")
    
    if product.deleted_at is None:
        product.deleted_at = datetime.now(timezone.utc)
        product.is_active = False
        db.commit()
        db.refresh(product)
        logger.info(f"Soft deleted product: {product.name} (id: {product.id})")
    
    return product


def get_product_price_range(db: Session, product_id: int) -> Tuple[Optional[Decimal], Optional[Decimal]]:
    """
    Get price range (min/max) for a product from its active variants
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        Tuple of (min_price, max_price) or (None, None) if no active variants
    """
    result = db.query(
        func.min(ProductVariant.price).label('min_price'),
        func.max(ProductVariant.price).label('max_price')
    ).filter(
        and_(
            ProductVariant.product_id == product_id,
            ProductVariant.is_active == True
        )
    ).first()
    
    if result and result.min_price is not None:
        return (result.min_price, result.max_price)
    
    return (None, None)


def has_stock(db: Session, product_id: int) -> bool:
    """
    Check if product has any active variants with stock
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        True if product has stock, False otherwise
    """
    count = db.query(ProductVariant).filter(
        and_(
            ProductVariant.product_id == product_id,
            ProductVariant.is_active == True,
            ProductVariant.stock_qty > 0
        )
    ).count()
    
    return count > 0


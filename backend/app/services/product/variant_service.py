"""
Product variant service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from decimal import Decimal

from app.models.product import Product, ProductVariant
from app.core.exceptions import NotFoundError, ConflictError
from app.schemas.product import ProductVariantCreate, ProductVariantUpdate
import logging

logger = logging.getLogger(__name__)


def create_variant(db: Session, product_id: int, variant_data: ProductVariantCreate) -> ProductVariant:
    """
    Create a new product variant
    
    Args:
        db: Database session
        product_id: Product ID
        variant_data: Variant creation data
        
    Returns:
        Created ProductVariant object
        
    Raises:
        NotFoundError: If product not found
        ConflictError: If label already exists for product or SKU already exists
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")
    
    # Check if label already exists for this product
    existing = db.query(ProductVariant).filter(
        and_(
            ProductVariant.product_id == product_id,
            ProductVariant.label == variant_data.label
        )
    ).first()
    
    if existing:
        raise ConflictError(f"Variant with label '{variant_data.label}' already exists for this product")
    
    # Check SKU uniqueness if provided
    if variant_data.sku:
        existing_sku = db.query(ProductVariant).filter(ProductVariant.sku == variant_data.sku).first()
        if existing_sku:
            raise ConflictError(f"Variant with SKU '{variant_data.sku}' already exists")
    
    # Create variant
    variant = ProductVariant(
        product_id=product_id,
        label=variant_data.label,
        price=variant_data.price,
        stock_qty=variant_data.stock_qty,
        sku=variant_data.sku,
        is_active=variant_data.is_active
    )
    
    db.add(variant)
    db.commit()
    db.refresh(variant)
    
    logger.info(f"Created variant: {variant.label} for product {product_id} (id: {variant.id})")
    return variant


def get_variant_by_id(db: Session, variant_id: int) -> Optional[ProductVariant]:
    """
    Get variant by ID
    
    Args:
        db: Database session
        variant_id: Variant ID
        
    Returns:
        ProductVariant object or None
    """
    return db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()


def list_variants(db: Session, product_id: int, include_inactive: bool = False) -> List[ProductVariant]:
    """
    List variants for a product
    
    Args:
        db: Database session
        product_id: Product ID
        include_inactive: Whether to include inactive variants
        
    Returns:
        List of ProductVariant objects
    """
    query = db.query(ProductVariant).filter(ProductVariant.product_id == product_id)
    
    if not include_inactive:
        query = query.filter(ProductVariant.is_active == True)
    
    return query.order_by(ProductVariant.created_at.asc()).all()


def update_variant(db: Session, variant_id: int, variant_data: ProductVariantUpdate) -> ProductVariant:
    """
    Update variant
    
    Args:
        db: Database session
        variant_id: Variant ID
        variant_data: Variant update data
        
    Returns:
        Updated ProductVariant object
        
    Raises:
        NotFoundError: If variant not found
        ConflictError: If new label/SKU already exists
    """
    variant = get_variant_by_id(db, variant_id)
    
    if not variant:
        raise NotFoundError(f"Variant with id {variant_id} not found")
    
    # Update label if provided
    if variant_data.label is not None:
        # Check if label already exists for this product (excluding current variant)
        existing = db.query(ProductVariant).filter(
            and_(
                ProductVariant.product_id == variant.product_id,
                ProductVariant.label == variant_data.label,
                ProductVariant.id != variant_id
            )
        ).first()
        
        if existing:
            raise ConflictError(f"Variant with label '{variant_data.label}' already exists for this product")
        
        variant.label = variant_data.label
    
    # Update other fields
    if variant_data.price is not None:
        variant.price = variant_data.price
    
    if variant_data.stock_qty is not None:
        variant.stock_qty = variant_data.stock_qty
    
    if variant_data.sku is not None:
        # Check SKU uniqueness if changed
        if variant_data.sku != variant.sku:
            existing_sku = db.query(ProductVariant).filter(
                and_(
                    ProductVariant.sku == variant_data.sku,
                    ProductVariant.id != variant_id
                )
            ).first()
            if existing_sku:
                raise ConflictError(f"Variant with SKU '{variant_data.sku}' already exists")
        variant.sku = variant_data.sku
    
    if variant_data.is_active is not None:
        variant.is_active = variant_data.is_active
    
    db.commit()
    db.refresh(variant)
    
    logger.info(f"Updated variant: {variant.label} (id: {variant.id})")
    return variant


def delete_variant(db: Session, variant_id: int) -> None:
    """
    Delete variant (hard delete)
    
    Args:
        db: Database session
        variant_id: Variant ID
        
    Raises:
        NotFoundError: If variant not found
    """
    variant = get_variant_by_id(db, variant_id)
    
    if not variant:
        raise NotFoundError(f"Variant with id {variant_id} not found")
    
    db.delete(variant)
    db.commit()
    
    logger.info(f"Deleted variant: {variant.label} (id: {variant_id})")


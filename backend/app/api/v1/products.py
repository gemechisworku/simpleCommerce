"""
Public product browsing endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from app.core.database import get_db
from app.schemas.product import ProductResponse, ProductListItemResponse
from app.schemas.common import ResponseModel, PaginatedResponse, PaginationMeta
from app.services.product import (
    get_product_by_slug,
    list_public_products,
    get_product_price_range,
    has_stock
)
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ProductListItemResponse], status_code=200)
async def list_products_public(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured products"),
    db: Session = Depends(get_db)
):
    """
    List products for public browsing
    
    Only shows active, non-deleted products with active variants.
    Includes price range and stock availability.
    """
    skip = (page - 1) * per_page
    products, total = list_public_products(
        db=db,
        skip=skip,
        limit=per_page,
        search=search,
        category_id=category_id,
        is_featured=is_featured
    )
    
    # Build response with price range and stock info
    product_items = []
    for product in products:
        price_min, price_max = get_product_price_range(db, product.id)
        stock_available = has_stock(db, product.id)
        
        # Get first image URL if available
        image_url = None
        if product.images:
            sorted_images = sorted(product.images, key=lambda x: x.sort_order)
            image_url = sorted_images[0].url if sorted_images else None
        
        product_item = ProductListItemResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            description=product.description,
            category_id=product.category_id,
            is_featured=product.is_featured,
            price_min=price_min,
            price_max=price_max,
            has_stock=stock_available,
            image_url=image_url,
            created_at=product.created_at
        )
        product_items.append(product_item)
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        data=product_items,
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )


@router.get("/{slug}", response_model=ResponseModel[ProductResponse], status_code=200)
async def get_product_by_slug_public(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get product detail by slug for public browsing
    
    Only returns active, non-deleted products with active variants.
    """
    product = get_product_by_slug(db, slug, include_deleted=False)
    
    if not product:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"Product with slug '{slug}' not found")
    
    # Filter to only show active variants in response
    # This is handled by the relationship, but we can ensure it
    active_variants = [v for v in product.variants if v.is_active]
    product.variants = active_variants
    
    return ResponseModel(data=ProductResponse.model_validate(product))


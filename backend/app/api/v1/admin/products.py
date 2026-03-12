"""
Admin product management endpoints
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductVariantCreate,
    ProductVariantUpdate,
    ProductVariantResponse
)
from app.schemas.common import ResponseModel, PaginatedResponse, PaginationMeta
from app.services.product import (
    create_product,
    get_product_by_id,
    list_products,
    update_product,
    delete_product,
    create_variant,
    get_variant_by_id,
    list_variants,
    update_variant,
    delete_variant
)
from app.core.config import settings

router = APIRouter()


# Product endpoints
@router.post("", response_model=ResponseModel[ProductResponse], status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    product_data: ProductCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new product with variants
    
    Requires admin role.
    """
    product = create_product(db, product_data)
    return ResponseModel(data=ProductResponse.model_validate(product))


@router.get("", response_model=PaginatedResponse[ProductResponse], status_code=status.HTTP_200_OK)
async def list_products_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all products with filters and pagination
    
    Requires admin role.
    """
    skip = (page - 1) * per_page
    products, total = list_products(
        db=db,
        skip=skip,
        limit=per_page,
        search=search,
        category_id=category_id,
        is_active=is_active,
        is_featured=is_featured,
        include_deleted=True
    )
    
    total_pages = (total + per_page - 1) // per_page

    # Build response with image_url from first image for each product
    result_data = []
    for p in products:
        resp = ProductResponse.model_validate(p)
        if p.images:
            sorted_images = sorted(p.images, key=lambda x: x.sort_order)
            first_url = sorted_images[0].url if sorted_images else None
            if first_url:
                resp = resp.model_copy(update={"image_url": first_url})
        result_data.append(resp)

    return PaginatedResponse(
        data=result_data,
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )


@router.get("/{product_id}", response_model=ResponseModel[ProductResponse], status_code=status.HTTP_200_OK)
async def get_product_endpoint(
    product_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get product detail by ID
    
    Requires admin role.
    """
    product = get_product_by_id(db, product_id, include_deleted=True)
    if not product:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"Product with id {product_id} not found")
    
    return ResponseModel(data=ProductResponse.model_validate(product))


@router.patch("/{product_id}", response_model=ResponseModel[ProductResponse], status_code=status.HTTP_200_OK)
async def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update product
    
    Requires admin role.
    """
    product = update_product(db, product_id, product_data)
    return ResponseModel(data=ProductResponse.model_validate(product))


@router.delete("/{product_id}", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK)
async def delete_product_endpoint(
    product_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Soft delete product
    
    Requires admin role.
    """
    product = delete_product(db, product_id)
    return ResponseModel(data={"message": f"Product '{product.name}' deleted successfully"})


# Variant endpoints
@router.post("/{product_id}/variants", response_model=ResponseModel[ProductVariantResponse], status_code=status.HTTP_201_CREATED)
async def create_variant_endpoint(
    product_id: int,
    variant_data: ProductVariantCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new product variant
    
    Requires admin role.
    """
    variant = create_variant(db, product_id, variant_data)
    return ResponseModel(data=ProductVariantResponse.model_validate(variant))


@router.get("/{product_id}/variants", response_model=ResponseModel[list[ProductVariantResponse]], status_code=status.HTTP_200_OK)
async def list_variants_endpoint(
    product_id: int,
    include_inactive: bool = Query(False, description="Include inactive variants"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List variants for a product
    
    Requires admin role.
    """
    variants = list_variants(db, product_id, include_inactive=include_inactive)
    return ResponseModel(data=[ProductVariantResponse.model_validate(v) for v in variants])


@router.get("/variants/{variant_id}", response_model=ResponseModel[ProductVariantResponse], status_code=status.HTTP_200_OK)
async def get_variant_endpoint(
    variant_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get variant detail by ID
    
    Requires admin role.
    """
    variant = get_variant_by_id(db, variant_id)
    if not variant:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"Variant with id {variant_id} not found")
    
    return ResponseModel(data=ProductVariantResponse.model_validate(variant))


@router.patch("/variants/{variant_id}", response_model=ResponseModel[ProductVariantResponse], status_code=status.HTTP_200_OK)
async def update_variant_endpoint(
    variant_id: int,
    variant_data: ProductVariantUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update variant
    
    Requires admin role.
    """
    variant = update_variant(db, variant_id, variant_data)
    return ResponseModel(data=ProductVariantResponse.model_validate(variant))


@router.delete("/variants/{variant_id}", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK)
async def delete_variant_endpoint(
    variant_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete variant (hard delete)
    
    Requires admin role.
    """
    delete_variant(db, variant_id)
    return ResponseModel(data={"message": "Variant deleted successfully"})


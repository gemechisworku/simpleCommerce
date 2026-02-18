"""
Product schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from uuid import UUID


# Product Variant Schemas
class ProductVariantCreate(BaseModel):
    """Create product variant schema"""
    label: str = Field(..., max_length=100, description="Variant label (e.g., '250g', '1kg pack')")
    price: Decimal = Field(..., ge=0, description="Variant price")
    stock_qty: int = Field(0, ge=0, description="Available stock quantity")
    sku: Optional[str] = Field(None, max_length=50, description="Stock keeping unit")
    is_active: bool = Field(True, description="Variant active status")


class ProductVariantUpdate(BaseModel):
    """Update product variant schema"""
    label: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    stock_qty: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class ProductVariantResponse(BaseModel):
    """Product variant response schema"""
    id: int
    product_id: int
    label: str
    price: Decimal
    stock_qty: int
    sku: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Product Image Schemas
class ProductImageCreate(BaseModel):
    """Create product image schema"""
    url: str = Field(..., max_length=500, description="Image URL")
    alt_text: Optional[str] = Field(None, max_length=200, description="Alt text for image")
    sort_order: int = Field(0, ge=0, description="Display sort order")


class ProductImageResponse(BaseModel):
    """Product image response schema"""
    id: int
    product_id: int
    url: str
    alt_text: Optional[str] = None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Product Schemas
class ProductCreate(BaseModel):
    """Create product schema"""
    name: str = Field(..., max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category_id: Optional[int] = Field(None, description="Category ID")
    is_active: bool = Field(True, description="Product active status")
    is_featured: bool = Field(False, description="Featured product flag")
    variants: List[ProductVariantCreate] = Field(default_factory=list, description="Product variants")


class ProductUpdate(BaseModel):
    """Update product schema"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class ProductResponse(BaseModel):
    """Product response schema"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_active: bool
    is_featured: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    variants: List[ProductVariantResponse] = []
    images: List[ProductImageResponse] = []
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class ProductListItemResponse(BaseModel):
    """Product list item response schema (simplified for listing)"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_featured: bool
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    has_stock: bool = False
    image_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


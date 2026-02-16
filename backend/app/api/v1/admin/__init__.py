"""
Admin API routes
"""
from fastapi import APIRouter
from app.api.v1.admin import products, product_images

admin_router = APIRouter()

# Include admin routers
admin_router.include_router(products.router, prefix="/products", tags=["admin-products"])
admin_router.include_router(product_images.router, tags=["admin-product-images"])


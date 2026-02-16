"""
Admin API routes
"""
from fastapi import APIRouter
from app.api.v1.admin import products, product_images, orders, delivery_zones, payment_methods

admin_router = APIRouter()

# Include admin routers
admin_router.include_router(products.router, prefix="/products", tags=["admin-products"])
admin_router.include_router(product_images.router, tags=["admin-product-images"])
admin_router.include_router(orders.router, prefix="/orders", tags=["admin-orders"])
admin_router.include_router(delivery_zones.router, prefix="/delivery-zones", tags=["admin-delivery-zones"])
admin_router.include_router(payment_methods.router, prefix="/payment-methods", tags=["admin-payment-methods"])


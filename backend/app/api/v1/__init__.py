"""
API v1 routes
"""
from fastapi import APIRouter
from app.api.v1 import health, auth, users

api_router = APIRouter()

# Include routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Import and include other routers as they are implemented
# from app.api.v1 import products, orders, payments, admin
# api_router.include_router(products.router, prefix="/products", tags=["products"])
# api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
# api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
# api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

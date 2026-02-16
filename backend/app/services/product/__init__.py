"""
Product services
"""
from app.services.product.product_service import (
    create_product,
    get_product_by_id,
    get_product_by_slug,
    list_products,
    list_public_products,
    update_product,
    delete_product,
    get_product_price_range,
    has_stock
)
from app.services.product.variant_service import (
    create_variant,
    get_variant_by_id,
    list_variants,
    update_variant,
    delete_variant
)


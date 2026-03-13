"""
Script to seed mock data for development/testing
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.category import Category
from app.models.product import Product, ProductVariant, ProductImage
from app.models.user import User, UserRole
from app.utils.helpers import generate_slug
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Superadmin seed - configurable via env (default for dev only)
SUPERADMIN_PHONE = os.environ.get("SUPERADMIN_PHONE", "+251911111111")
SUPERADMIN_EMAIL = os.environ.get("SUPERADMIN_EMAIL", "admin@simplecommerce.local")
SUPERADMIN_FIRST_NAME = os.environ.get("SUPERADMIN_FIRST_NAME", "Super")
SUPERADMIN_LAST_NAME = os.environ.get("SUPERADMIN_LAST_NAME", "Admin")


def seed_superadmin(db: Session):
    """Seed first admin user for initial access. Login via phone OTP at /login."""
    logger.info("Seeding superadmin user...")

    existing = db.query(User).filter(User.phone == SUPERADMIN_PHONE).first()
    if existing:
        if existing.role == UserRole.ADMIN:
            logger.info(f"Superadmin already exists: {SUPERADMIN_PHONE}, skipping...")
            return
        # Upgrade existing user to admin if they're not
        existing.role = UserRole.ADMIN
        existing.first_name = SUPERADMIN_FIRST_NAME
        existing.last_name = SUPERADMIN_LAST_NAME
        existing.email = SUPERADMIN_EMAIL or existing.email
        db.commit()
        logger.info(f"Upgraded user to admin: {SUPERADMIN_PHONE}")
        return

    # Check if email is taken (email must be unique)
    admin_email = SUPERADMIN_EMAIL
    if admin_email:
        email_taken = db.query(User).filter(User.email == admin_email).first()
        if email_taken:
            logger.warning(f"Email {admin_email} already in use, creating admin without email")
            admin_email = None

    admin = User(
        phone=SUPERADMIN_PHONE,
        phone_verified=True,
        email=admin_email,
        first_name=SUPERADMIN_FIRST_NAME,
        last_name=SUPERADMIN_LAST_NAME,
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    logger.info(f"Created superadmin: {SUPERADMIN_PHONE} | Login at /login, then go to /admin (OTP in backend logs for dev)")


def seed_categories(db: Session):
    """Seed categories"""
    logger.info("Seeding categories...")
    
    categories_data = [
        {"name": "Coffee", "description": "Premium coffee beans and ground coffee"},
        {"name": "Tea", "description": "Various types of tea"},
        {"name": "Spices", "description": "Ethiopian spices and seasonings"},
        {"name": "Honey", "description": "Natural honey products"},
        {"name": "Grains", "description": "Cereals and grains"},
    ]
    
    for cat_data in categories_data:
        # Check if category already exists
        existing = db.query(Category).filter(Category.slug == generate_slug(cat_data["name"])).first()
        if existing:
            logger.info(f"Category '{cat_data['name']}' already exists, skipping...")
            continue
        
        category = Category(
            name=cat_data["name"],
            slug=generate_slug(cat_data["name"]),
            description=cat_data["description"],
            is_active=True,
            sort_order=len(categories_data) - categories_data.index(cat_data)
        )
        db.add(category)
    
    db.commit()
    logger.info("Categories seeded successfully")


def seed_products(db: Session):
    """Seed products with variants"""
    logger.info("Seeding products...")
    
    # Get categories
    coffee_cat = db.query(Category).filter(Category.slug == "coffee").first()
    tea_cat = db.query(Category).filter(Category.slug == "tea").first()
    spices_cat = db.query(Category).filter(Category.slug == "spices").first()
    honey_cat = db.query(Category).filter(Category.slug == "honey").first()
    grains_cat = db.query(Category).filter(Category.slug == "grains").first()
    
    products_data = [
        {
            "name": "Ethiopian Yirgacheffe Coffee Beans",
            "description": "Premium single-origin coffee beans from Yirgacheffe region. Known for its bright acidity and floral notes.",
            "category": coffee_cat,
            "is_featured": True,
            "variants": [
                {"label": "250g", "price": Decimal("450.00"), "stock_qty": 50, "sku": "COFFEE-YIRG-250"},
                {"label": "500g", "price": Decimal("850.00"), "stock_qty": 30, "sku": "COFFEE-YIRG-500"},
                {"label": "1kg", "price": Decimal("1600.00"), "stock_qty": 20, "sku": "COFFEE-YIRG-1KG"},
            ]
        },
        {
            "name": "Sidamo Coffee Beans",
            "description": "Rich and full-bodied coffee beans from Sidamo region. Perfect for espresso.",
            "category": coffee_cat,
            "is_featured": True,
            "variants": [
                {"label": "250g", "price": Decimal("420.00"), "stock_qty": 40, "sku": "COFFEE-SID-250"},
                {"label": "500g", "price": Decimal("800.00"), "stock_qty": 25, "sku": "COFFEE-SID-500"},
                {"label": "1kg", "price": Decimal("1500.00"), "stock_qty": 15, "sku": "COFFEE-SID-1KG"},
            ]
        },
        {
            "name": "Harrar Coffee Beans",
            "description": "Wild and fruity coffee beans from Harrar region. Unique wine-like flavor.",
            "category": coffee_cat,
            "is_featured": False,
            "variants": [
                {"label": "250g", "price": Decimal("480.00"), "stock_qty": 35, "sku": "COFFEE-HAR-250"},
                {"label": "500g", "price": Decimal("900.00"), "stock_qty": 20, "sku": "COFFEE-HAR-500"},
            ]
        },
        {
            "name": "Ethiopian Green Tea",
            "description": "High-quality green tea leaves from Ethiopian highlands.",
            "category": tea_cat,
            "is_featured": False,
            "variants": [
                {"label": "100g", "price": Decimal("250.00"), "stock_qty": 60, "sku": "TEA-GREEN-100"},
                {"label": "250g", "price": Decimal("550.00"), "stock_qty": 40, "sku": "TEA-GREEN-250"},
            ]
        },
        {
            "name": "Black Tea",
            "description": "Traditional Ethiopian black tea with rich flavor.",
            "category": tea_cat,
            "is_featured": False,
            "variants": [
                {"label": "100g", "price": Decimal("200.00"), "stock_qty": 70, "sku": "TEA-BLACK-100"},
                {"label": "250g", "price": Decimal("450.00"), "stock_qty": 50, "sku": "TEA-BLACK-250"},
            ]
        },
        {
            "name": "Berbere Spice Mix",
            "description": "Traditional Ethiopian spice blend. Essential for Ethiopian cuisine.",
            "category": spices_cat,
            "is_featured": True,
            "variants": [
                {"label": "100g", "price": Decimal("180.00"), "stock_qty": 80, "sku": "SPICE-BERB-100"},
                {"label": "250g", "price": Decimal("400.00"), "stock_qty": 50, "sku": "SPICE-BERB-250"},
                {"label": "500g", "price": Decimal("750.00"), "stock_qty": 30, "sku": "SPICE-BERB-500"},
            ]
        },
        {
            "name": "Mitmita Spice",
            "description": "Hot and spicy Ethiopian chili powder. Use with caution!",
            "category": spices_cat,
            "is_featured": False,
            "variants": [
                {"label": "50g", "price": Decimal("150.00"), "stock_qty": 90, "sku": "SPICE-MITM-50"},
                {"label": "100g", "price": Decimal("280.00"), "stock_qty": 60, "sku": "SPICE-MITM-100"},
            ]
        },
        {
            "name": "Turmeric Powder",
            "description": "Pure turmeric powder. Great for cooking and health benefits.",
            "category": spices_cat,
            "is_featured": False,
            "variants": [
                {"label": "100g", "price": Decimal("120.00"), "stock_qty": 100, "sku": "SPICE-TURM-100"},
                {"label": "250g", "price": Decimal("280.00"), "stock_qty": 70, "sku": "SPICE-TURM-250"},
            ]
        },
        {
            "name": "Wild Honey",
            "description": "Pure wild honey collected from Ethiopian forests. Natural and unprocessed.",
            "category": honey_cat,
            "is_featured": True,
            "variants": [
                {"label": "250g", "price": Decimal("350.00"), "stock_qty": 45, "sku": "HONEY-WILD-250"},
                {"label": "500g", "price": Decimal("650.00"), "stock_qty": 30, "sku": "HONEY-WILD-500"},
                {"label": "1kg", "price": Decimal("1200.00"), "stock_qty": 20, "sku": "HONEY-WILD-1KG"},
            ]
        },
        {
            "name": "Teff Flour",
            "description": "Traditional Ethiopian teff flour. Gluten-free and nutritious.",
            "category": grains_cat,
            "is_featured": False,
            "variants": [
                {"label": "500g", "price": Decimal("300.00"), "stock_qty": 55, "sku": "GRAIN-TEFF-500"},
                {"label": "1kg", "price": Decimal("550.00"), "stock_qty": 35, "sku": "GRAIN-TEFF-1KG"},
            ]
        },
        {
            "name": "Quinoa",
            "description": "High-quality quinoa grains. Perfect for healthy meals.",
            "category": grains_cat,
            "is_featured": False,
            "variants": [
                {"label": "500g", "price": Decimal("450.00"), "stock_qty": 40, "sku": "GRAIN-QUIN-500"},
                {"label": "1kg", "price": Decimal("850.00"), "stock_qty": 25, "sku": "GRAIN-QUIN-1KG"},
            ]
        },
    ]
    
    for prod_data in products_data:
        # Check if product already exists
        existing = db.query(Product).filter(Product.slug == generate_slug(prod_data["name"])).first()
        if existing:
            logger.info(f"Product '{prod_data['name']}' already exists, skipping...")
            continue
        
        product = Product(
            name=prod_data["name"],
            slug=generate_slug(prod_data["name"]),
            description=prod_data["description"],
            category_id=prod_data["category"].id if prod_data["category"] else None,
            is_active=True,
            is_featured=prod_data.get("is_featured", False)
        )
        db.add(product)
        db.flush()  # Get product.id
        
        # Add variants
        for variant_data in prod_data["variants"]:
            variant = ProductVariant(
                product_id=product.id,
                label=variant_data["label"],
                price=variant_data["price"],
                stock_qty=variant_data["stock_qty"],
                sku=variant_data["sku"],
                is_active=True
            )
            db.add(variant)
        
        db.commit()
        logger.info(f"Created product: {prod_data['name']}")
    
    logger.info("Products seeded successfully")


# Product image URLs - use Lorem Picsum (reliable hotlinking, no 403)
# Format: https://picsum.photos/seed/{slug}/800/800 for consistent images per product
def get_product_image_url(slug: str) -> str:
    """Get placeholder image URL for product (Picsum allows hotlinking)"""
    return f"https://picsum.photos/seed/{slug}/800/800"


def seed_product_images(db: Session):
    """Seed product images for existing products"""
    logger.info("Seeding product images...")

    products = db.query(Product).filter(Product.deleted_at.is_(None)).all()
    for product in products:
        existing_images = db.query(ProductImage).filter(ProductImage.product_id == product.id).all()

        # Replace Unsplash URLs (can cause 403) with Picsum
        if existing_images and "unsplash" in (existing_images[0].url or ""):
            for img in existing_images:
                img.url = get_product_image_url(product.slug)
            db.commit()
            logger.info(f"Updated image URL for product: {product.name}")
            continue

        if existing_images:
            logger.info(f"Product '{product.name}' already has images, skipping...")
            continue

        url = get_product_image_url(product.slug)
        image = ProductImage(
            product_id=product.id,
            url=url,
            alt_text=product.name,
            sort_order=0,
        )
        db.add(image)
        db.commit()
        logger.info(f"Added image for product: {product.name}")

    logger.info("Product images seeded successfully")


def main():
    """Main seeding function. Set SEED_ADMIN_ONLY=1 to only create/upgrade superadmin (for production)."""
    admin_only = os.environ.get("SEED_ADMIN_ONLY", "").strip().lower() in ("1", "true", "yes")
    db: Session = SessionLocal()
    try:
        if admin_only:
            logger.info("Starting seed (admin only, no mock products)...")
        else:
            logger.info("Starting mock data seeding...")
        seed_superadmin(db)
        if not admin_only:
            seed_categories(db)
            seed_products(db)
            seed_product_images(db)
        logger.info("Seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


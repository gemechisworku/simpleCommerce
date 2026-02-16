"""
Product models
"""
from sqlalchemy import Column, String, Text, Boolean, BigInteger, ForeignKey, DateTime, Integer, Numeric, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Product(Base):
    """Product model"""
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(BigInteger, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, slug={self.slug})>"


class ProductVariant(Base):
    """Product variant model"""
    __tablename__ = "product_variants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock_qty = Column(Integer, nullable=False, default=0)
    sku = Column(String(50), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="variants")

    # Constraints
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_non_negative"),
        CheckConstraint("stock_qty >= 0", name="check_stock_non_negative"),
        # Unique constraint: variant label must be unique per product
        # This will be handled at the database level via migration
    )

    def __repr__(self):
        return f"<ProductVariant(id={self.id}, product_id={self.product_id}, label={self.label}, price={self.price})>"


class ProductImage(Base):
    """Product image model"""
    __tablename__ = "product_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(200), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, url={self.url})>"


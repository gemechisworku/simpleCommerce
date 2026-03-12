"""
Admin product image management endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.models.product import Product, ProductImage
from app.schemas.product import ProductImageResponse, ProductImageCreate
from app.schemas.common import ResponseModel
from app.core.exceptions import NotFoundError, BusinessRuleError
from app.core.storage import minio_client, ensure_bucket_exists
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/products/{product_id}/images", response_model=ResponseModel[ProductImageResponse], status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    alt_text: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Upload product image
    
    Requires admin role.
    Validates file type (jpg/png) and size (max 5MB).
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")
    
    # Validate file type
    content_type = file.content_type
    if content_type not in settings.ALLOWED_FILE_TYPES.split(","):
        raise BusinessRuleError(f"Invalid file type. Allowed types: {settings.ALLOWED_FILE_TYPES}")
    
    # Validate file size (5MB max)
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise BusinessRuleError(f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB")
    
    # Generate unique filename
    import uuid
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"products/{product_id}/{uuid.uuid4()}.{file_extension}"
    
    # Upload to MinIO (put_object expects a file-like object; ensure bucket exists)
    try:
        from io import BytesIO
        ensure_bucket_exists(settings.MINIO_BUCKET_NAME)
        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=filename,
            data=BytesIO(file_content),
            length=len(file_content),
            content_type=content_type
        )
        
        # Generate URL (in production, use proper CDN URL)
        image_url = f"/storage/{settings.MINIO_BUCKET_NAME}/{filename}"
        
        # Get current max sort_order for this product
        max_sort = db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).count()
        
        # Create image record
        image = ProductImage(
            product_id=product_id,
            url=image_url,
            alt_text=alt_text or f"{product.name} image",
            sort_order=max_sort
        )
        
        db.add(image)
        db.commit()
        db.refresh(image)
        
        logger.info(f"Uploaded image for product {product_id}: {filename}")
        return ResponseModel(data=ProductImageResponse.model_validate(image))
        
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise BusinessRuleError(f"Failed to upload image: {str(e)}")


@router.get("/products/{product_id}/images", response_model=ResponseModel[List[ProductImageResponse]], status_code=status.HTTP_200_OK)
async def list_product_images(
    product_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List images for a product
    
    Requires admin role.
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")
    
    images = db.query(ProductImage).filter(
        ProductImage.product_id == product_id
    ).order_by(ProductImage.sort_order.asc()).all()
    
    return ResponseModel(data=[ProductImageResponse.model_validate(img) for img in images])


@router.delete("/products/{product_id}/images/{image_id}", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK)
async def delete_product_image(
    product_id: int,
    image_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete product image
    
    Requires admin role.
    Removes image from storage and database.
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")
    
    # Get image
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id,
        ProductImage.product_id == product_id
    ).first()
    
    if not image:
        raise NotFoundError(f"Image with id {image_id} not found for product {product_id}")
    
    # Extract filename from URL
    filename = image.url.replace(f"/storage/{settings.MINIO_BUCKET_NAME}/", "")
    
    # Delete from MinIO
    try:
        minio_client.remove_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=filename
        )
    except Exception as e:
        logger.warning(f"Error deleting image from storage: {str(e)}")
    
    # Delete from database
    db.delete(image)
    db.commit()
    
    logger.info(f"Deleted image {image_id} for product {product_id}")
    return ResponseModel(data={"message": "Image deleted successfully"})


"""
MinIO/S3 storage client
"""
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL
)


def ensure_bucket_exists(bucket_name: str = None) -> bool:
    """
    Ensure the bucket exists, create if it doesn't
    
    Args:
        bucket_name: Bucket name (defaults to settings.MINIO_BUCKET_NAME)
        
    Returns:
        True if bucket exists or was created, False otherwise
    """
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    
    try:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
            logger.info(f"Created bucket: {bucket}")
        return True
    except S3Error as e:
        logger.error(f"Error ensuring bucket exists: {e}")
        return False


def upload_file(
    file_data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
    bucket_name: str = None
) -> Optional[str]:
    """
    Upload file to MinIO/S3
    
    Args:
        file_data: File data as bytes
        object_name: Object name (path) in bucket
        content_type: MIME type of file
        bucket_name: Bucket name (defaults to settings.MINIO_BUCKET_NAME)
        
    Returns:
        URL of uploaded file if successful, None otherwise
    """
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    
    try:
        # Ensure bucket exists
        ensure_bucket_exists(bucket)
        
        # Upload file
        from io import BytesIO
        file_stream = BytesIO(file_data)
        
        minio_client.put_object(
            bucket,
            object_name,
            file_stream,
            length=len(file_data),
            content_type=content_type
        )
        
        # Construct URL
        protocol = "https" if settings.MINIO_USE_SSL else "http"
        url = f"{protocol}://{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"
        
        logger.info(f"Uploaded file: {object_name} to bucket: {bucket}")
        return url
        
    except S3Error as e:
        logger.error(f"Error uploading file: {e}")
        return None


def delete_file(object_name: str, bucket_name: str = None) -> bool:
    """
    Delete file from MinIO/S3
    
    Args:
        object_name: Object name (path) in bucket
        bucket_name: Bucket name (defaults to settings.MINIO_BUCKET_NAME)
        
    Returns:
        True if deleted successfully, False otherwise
    """
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    
    try:
        minio_client.remove_object(bucket, object_name)
        logger.info(f"Deleted file: {object_name} from bucket: {bucket}")
        return True
    except S3Error as e:
        logger.error(f"Error deleting file: {e}")
        return False


def get_file_url(object_name: str, bucket_name: str = None) -> str:
    """
    Get URL for a file in MinIO/S3
    
    Args:
        object_name: Object name (path) in bucket
        bucket_name: Bucket name (defaults to settings.MINIO_BUCKET_NAME)
        
    Returns:
        URL string
    """
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    protocol = "https" if settings.MINIO_USE_SSL else "http"
    return f"{protocol}://{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"


"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://simplecommerce:simplecommerce@db:5432/simplecommerce"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "simplecommerce-uploads"
    MINIO_USE_SSL: bool = False
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # OTP
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    
    # Rate Limiting
    OTP_RATE_LIMIT_WINDOW_MINUTES: int = 15  # Time window for rate limiting
    OTP_RATE_LIMIT_MAX_PER_IDENTIFIER: int = 3  # Max OTP requests per phone/email
    OTP_RATE_LIMIT_MAX_PER_IP: int = 5  # Max OTP requests per IP address
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_FILE_TYPES: str = "image/jpeg,image/png,image/jpg"
    # Payment documents: images + PDF
    PAYMENT_ALLOWED_FILE_TYPES: str = "image/jpeg,image/png,image/jpg,application/pdf"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Telegram Mini App (optional)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_INIT_DATA_MAX_AGE_SECONDS: int = 86400  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


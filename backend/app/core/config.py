"""
Application configuration
"""
import json
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


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
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:3001"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Accept JSON array, comma-separated string, or single URL (e.g. from Railway env)."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return ["http://localhost:3000", "http://localhost:3001"]
            if s.startswith("["):
                try:
                    return json.loads(s)
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in s.split(",") if origin.strip()]
        return ["http://localhost:3000", "http://localhost:3001"]
    
    # OTP
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    # OTP delivery: "twilio" to send SMS in production; "" or "log" = log only (dev/default)
    OTP_SMS_PROVIDER: str = ""
    # Twilio (when OTP_SMS_PROVIDER=twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""  # E.164, e.g. +1234567890
    
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

    # Telegram Mini App and OTP (optional)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""  # Bot username without @, for t.me/BotUsername links
    TELEGRAM_INIT_DATA_MAX_AGE_SECONDS: int = 86400  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


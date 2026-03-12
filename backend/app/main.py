"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import HTTPException
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1 import api_router
from app.core.exceptions import AppException
import logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="simpleCommerce API",
    description="Commerce & Order Operations Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
# Allow Vercel frontend in all environments; in development also allow tunnels (ngrok, Cloudflare)
_cors_origin_regex = r"https://.*\.vercel\.app"
if settings.ENVIRONMENT == "development":
    _cors_origin_regex = r"https://.*\.(vercel\.app|ngrok-free\.app|ngrok-free\.dev|trycloudflare\.com)"

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/storage/{file_path:path}")
async def serve_storage(file_path: str):
    """
    Serve files from MinIO storage. URL: /storage/{bucket_name}/{object_key}.
    Only the configured bucket is allowed.
    """
    parts = file_path.strip("/").split("/", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=404, detail="Not found")
    bucket_name, object_name = parts
    if bucket_name != settings.MINIO_BUCKET_NAME or not object_name:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        from app.core.storage import minio_client
        response = minio_client.get_object(bucket_name, object_name)
        if object_name.lower().endswith(".pdf"):
            media_type = "application/pdf"
        elif object_name.lower().endswith(".png"):
            media_type = "image/png"
        elif object_name.lower().endswith((".jpg", ".jpeg")):
            media_type = "image/jpeg"
        else:
            media_type = "application/octet-stream"

        def iter_chunks():
            try:
                chunk_size = 32 * 1024
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            finally:
                response.close()
                response.release_conn()

        return StreamingResponse(
            iter_chunks(),
            media_type=media_type,
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        logger.warning(f"Storage get failed for {bucket_name}/{object_name}: {e}")
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/health")
async def health_check():
    """Health check endpoint (root level)"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "simpleCommerce API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting simpleCommerce API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    # Ensure MinIO bucket exists (create if missing); non-fatal if MinIO is unavailable
    try:
        from app.core.storage import ensure_bucket_exists
        if ensure_bucket_exists():
            logger.info("MinIO bucket ready")
        else:
            logger.warning("MinIO bucket check failed (bucket may be created on first upload)")
    except Exception as e:
        logger.warning(f"MinIO startup check skipped: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down simpleCommerce API")


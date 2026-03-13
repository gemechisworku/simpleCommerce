"""
FastAPI Application Entry Point
"""
import re
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1 import api_router
from app.core.exceptions import AppException

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

# CORS: same origin check as CORSMiddleware (explicit list + regex)
_CORS_ORIGIN_REGEX = re.compile(r"^https://.*\.vercel\.app$")
if settings.ENVIRONMENT == "development":
    _CORS_ORIGIN_REGEX = re.compile(r"^https://.*\.(vercel\.app|ngrok-free\.app|ngrok-free\.dev|trycloudflare\.com)$")


def _cors_headers_for_request(request: Request) -> dict:
    """Return CORS headers for the request's Origin if allowed; else empty dict."""
    origin = request.headers.get("origin")
    if not origin:
        return {}
    origin = origin.strip()
    if origin in settings.CORS_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    if _CORS_ORIGIN_REGEX.fullmatch(origin):
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    return {}


# CORS middleware (for successful and 4xx responses that go through the app)
_cors_origin_regex_str = r"https://.*\.vercel\.app"
if settings.ENVIRONMENT == "development":
    _cors_origin_regex_str = r"https://.*\.(vercel\.app|ngrok-free\.app|ngrok-free\.dev|trycloudflare\.com)"
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=_cors_origin_regex_str,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Global exception handler for app exceptions (4xx, etc.)
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


# Handlers for 500 and unhandled Exception: add CORS headers so the browser
# receives a valid CORS response (otherwise Starlette's ServerErrorMiddleware
# responds outside the CORS middleware and the browser reports "No Access-Control-Allow-Origin").
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler_with_cors(request: Request, exc: StarletteHTTPException):
    """Ensure CORS headers on HTTPException responses (e.g. 500)."""
    headers = dict(_cors_headers_for_request(request))
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail},
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler_with_cors(request: Request, exc: RequestValidationError):
    """Ensure CORS headers on 422 validation error responses."""
    headers = dict(_cors_headers_for_request(request))
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers=headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return 500 with CORS headers so the client sees a CORS-valid response and optional error detail."""
    logger.exception("Unhandled exception: %s", exc)
    headers = dict(_cors_headers_for_request(request))
    content = {
        "code": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred.",
    }
    if settings.DEBUG:
        content["detail"] = str(exc)
    return JSONResponse(
        status_code=500,
        content=content,
        headers=headers,
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
    logger.info(f"CORS allowed origins: {len(settings.CORS_ORIGINS)} explicit; regex *.vercel.app enabled")
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


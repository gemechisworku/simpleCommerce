"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down simpleCommerce API")


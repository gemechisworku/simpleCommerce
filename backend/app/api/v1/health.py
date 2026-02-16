"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.storage import minio_client
from app.schemas.common import ResponseModel
from typing import Dict, Any

router = APIRouter()


@router.get("/health")
async def health_check() -> ResponseModel[Dict[str, Any]]:
    """
    Basic health check endpoint
    """
    return ResponseModel(data={
        "status": "healthy",
        "service": "simpleCommerce API"
    })


@router.get("/health/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db)
) -> ResponseModel[Dict[str, Any]]:
    """
    Detailed health check with database and storage connectivity
    """
    health_status = {
        "status": "healthy",
        "service": "simpleCommerce API",
        "database": "unknown",
        "storage": "unknown"
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check storage connection
    try:
        # Try to list buckets (lightweight operation)
        minio_client.list_buckets()
        health_status["storage"] = "connected"
    except Exception as e:
        health_status["storage"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return ResponseModel(data=health_status)


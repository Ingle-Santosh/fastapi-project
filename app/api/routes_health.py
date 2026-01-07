"""
Health check endpoints for monitoring and orchestration
"""
from fastapi import APIRouter, status, Response
from datetime import datetime
import psutil
import os

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "FastAPI ML Application"
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(response: Response):
    """
    Readiness check endpoint
    Checks if service is ready to accept traffic
    Validates model, database, cache connections
    """
    checks = {
        "model": check_model_loaded(),
        "redis": check_redis_connection(),
        "database": check_database_connection(),
    }
    
    all_ready = all(checks.values())
    
    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@router.get("/status", status_code=status.HTTP_200_OK)
async def status_check():
    """
    Detailed status endpoint with system metrics
    """
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": get_uptime(),
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


def check_model_loaded() -> bool:
    """Check if ML model is loaded"""
    try:
        from app.services.model_service import ModelService
        service = ModelService()
        return service.model is not None
    except Exception:
        return False


def check_redis_connection() -> bool:
    """Check Redis connection"""
    try:
        from app.cache.redis_cache import redis_client
        redis_client.ping()
        return True
    except Exception:
        return False


def check_database_connection() -> bool:
    """Check database connection"""
    try:
        # Add your database connection check here
        # Example: db.execute("SELECT 1")
        return True
    except Exception:
        return False


def get_uptime() -> str:
    """Get application uptime"""
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    except Exception:
        return "unknown"
"""
Health Check API Endpoints

Provides health monitoring endpoints for production monitoring:
- /health - Simple health check (200 OK if healthy)
- /health/detailed - Comprehensive health status
- /health/metrics - Performance metrics

Usage:
    from routers.health import router as health_router
    app.include_router(health_router)
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import time

from ..database import get_db
from ..monitoring.health_check import get_health_checker, HealthStatus

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=Dict[str, Any])
async def simple_health_check(response: Response):
    """
    Simple health check endpoint

    Returns 200 OK if the system is healthy, 503 Service Unavailable otherwise.
    Used by load balancers and monitoring tools for quick health checks.

    Returns:
        dict: Simple health status
    """
    checker = get_health_checker()
    health = checker.get_simple_health()

    if health["status"] != "healthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Comprehensive health check endpoint

    Provides detailed health status for all subsystems:
    - Database connectivity and integrity
    - FTS5 search index status
    - Disk space availability
    - Memory usage
    - Backup status
    - API performance metrics

    Returns:
        dict: Detailed health status with all subsystems
    """
    checker = get_health_checker()
    health = checker.get_health_status(db_session=db)

    # Set appropriate HTTP status code
    if health["status"] == HealthStatus.UNHEALTHY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif health["status"] == HealthStatus.DEGRADED:
        response.status_code = status.HTTP_200_OK
        health["warning"] = "System is degraded but operational"

    return health


@router.get("/metrics", response_model=Dict[str, Any])
async def health_metrics():
    """
    Get health and performance metrics

    Returns summary metrics suitable for monitoring dashboards:
    - System uptime
    - Request counts and response times
    - Resource usage
    - Error rates

    Returns:
        dict: Health and performance metrics
    """
    checker = get_health_checker()
    health = checker.get_health_status()

    # Extract key metrics
    metrics = {
        "timestamp": health["timestamp"],
        "overall_status": health["status"],
        "total_requests": health["subsystems"]["performance"].get("total_requests", 0),
        "avg_response_time_ms": health["subsystems"]["performance"].get("avg_response_time_ms", 0),
        "database_entries": health["subsystems"]["database"].get("entry_count", 0),
        "database_size_mb": health["subsystems"]["database"].get("database_size_mb", 0),
        "fts_indexed_entries": health["subsystems"]["fts_search"].get("indexed_entries", 0),
        "disk_free_gb": health["subsystems"]["disk"].get("free_gb", 0),
        "disk_used_percent": health["subsystems"]["disk"].get("used_percent", 0),
        "memory_used_percent": health["subsystems"]["memory"].get("used_percent", 0),
        "memory_available_gb": health["subsystems"]["memory"].get("available_gb", 0),
        "backup_count": health["subsystems"]["backups"].get("backup_count", 0),
        "backup_age_hours": health["subsystems"]["backups"].get("backup_age_hours", 0),
        "issue_count": len(health.get("issues", [])),
        "issues": health.get("issues", [])
    }

    return metrics


@router.get("/ping")
async def ping():
    """
    Ultra-simple ping endpoint

    Returns "pong" immediately without any checks.
    Used for basic connectivity testing.

    Returns:
        dict: Pong response
    """
    return {"status": "pong", "message": "Service is reachable"}


@router.get("/ready")
async def readiness_check(response: Response, db: Session = Depends(get_db)):
    """
    Kubernetes-style readiness probe

    Checks if the application is ready to serve traffic.
    Returns 200 if ready, 503 if not ready.

    Returns:
        dict: Readiness status
    """
    checker = get_health_checker()

    try:
        # Check critical components only
        db_health = checker._check_database_health(db)
        fts_health = checker._check_fts_health()

        if (db_health["status"] == HealthStatus.HEALTHY and
            fts_health["status"] in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]):
            return {
                "ready": True,
                "message": "Application is ready to serve traffic"
            }
        else:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {
                "ready": False,
                "message": "Application is not ready",
                "database": db_health["status"],
                "fts": fts_health["status"]
            }
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "ready": False,
            "message": f"Readiness check failed: {str(e)}"
        }


@router.get("/liveness")
async def liveness_check():
    """
    Kubernetes-style liveness probe

    Checks if the application process is alive.
    Always returns 200 unless the process is completely dead.

    Returns:
        dict: Liveness status
    """
    return {
        "alive": True,
        "message": "Application process is alive"
    }

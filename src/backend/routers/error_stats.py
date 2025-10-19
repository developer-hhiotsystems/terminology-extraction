"""
Error Statistics API Endpoints

Provides error tracking statistics for monitoring.

Usage:
    from routers.error_stats import router as error_stats_router
    app.include_router(error_stats_router)
"""

from fastapi import APIRouter
from typing import Dict, Any

from ..monitoring.error_tracking import get_error_tracker

router = APIRouter(prefix="/api/errors", tags=["Error Stats"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_error_stats():
    """
    Get error tracking statistics

    Returns error counts, rates, and types for monitoring dashboards.

    Returns:
        dict: Error statistics including counts, rates, and breakdown by type
    """
    tracker = get_error_tracker()
    return tracker.get_stats()


@router.post("/stats/reset")
async def reset_error_stats():
    """
    Reset error statistics

    Resets all error counters. Useful for testing or after resolving issues.

    Returns:
        dict: Confirmation message
    """
    tracker = get_error_tracker()
    tracker.reset()

    return {
        "message": "Error statistics reset successfully",
        "status": "success"
    }

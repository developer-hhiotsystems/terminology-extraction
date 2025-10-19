"""
Performance Monitoring API

Provides endpoints for performance metrics and analysis.

Usage:
    from routers.performance import router as performance_router
    app.include_router(performance_router)
"""

from fastapi import APIRouter
from typing import Dict, Any, Optional

from ..monitoring.performance_monitor import get_performance_monitor

router = APIRouter(prefix="/api/performance", tags=["Performance"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_performance_stats():
    """
    Get comprehensive performance statistics

    Returns detailed performance metrics including:
    - Query performance (database)
    - Endpoint latency (API)
    - Cache hit/miss rates
    - Memory usage
    - Slow operations

    Returns:
        dict: Complete performance statistics
    """
    perf = get_performance_monitor()
    return perf.get_comprehensive_stats()


@router.get("/queries", response_model=Dict[str, Any])
async def get_query_performance(query_name: Optional[str] = None):
    """
    Get database query performance statistics

    Args:
        query_name: Optional specific query name

    Returns:
        dict: Query performance metrics
    """
    perf = get_performance_monitor()
    return perf.get_query_stats(query_name)


@router.get("/endpoints", response_model=Dict[str, Any])
async def get_endpoint_performance(endpoint: Optional[str] = None):
    """
    Get API endpoint performance statistics

    Args:
        endpoint: Optional specific endpoint

    Returns:
        dict: Endpoint performance metrics
    """
    perf = get_performance_monitor()
    return perf.get_endpoint_stats(endpoint)


@router.get("/cache", response_model=Dict[str, Any])
async def get_cache_performance():
    """
    Get cache performance statistics

    Returns:
        dict: Cache hit/miss statistics
    """
    perf = get_performance_monitor()
    return perf.get_cache_stats()


@router.get("/memory", response_model=Dict[str, Any])
async def get_memory_usage():
    """
    Get memory usage statistics

    Returns:
        dict: Memory usage metrics
    """
    perf = get_performance_monitor()
    return perf.get_memory_stats()


@router.get("/slow-queries", response_model=list)
async def get_slow_queries(limit: int = 10):
    """
    Get recent slow database queries

    Args:
        limit: Number of results to return (default: 10)

    Returns:
        list: Recent slow queries with durations
    """
    perf = get_performance_monitor()
    return perf.get_slow_queries(limit)


@router.get("/slow-endpoints", response_model=list)
async def get_slow_endpoints(limit: int = 10):
    """
    Get recent slow API endpoints

    Args:
        limit: Number of results to return (default: 10)

    Returns:
        list: Recent slow endpoints with durations
    """
    perf = get_performance_monitor()
    return perf.get_slow_endpoints(limit)


@router.post("/reset")
async def reset_performance_metrics():
    """
    Reset all performance metrics

    Clears all collected performance data.
    Useful after resolving performance issues.

    Returns:
        dict: Success message
    """
    perf = get_performance_monitor()
    perf.reset()

    return {
        "message": "Performance metrics reset successfully",
        "status": "success"
    }

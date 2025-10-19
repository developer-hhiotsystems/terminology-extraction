"""
Cache Administration API

Provides endpoints for cache management:
- Get cache statistics
- Clear cache entries
- Invalidate specific cache keys

Usage:
    from routers.cache_admin import router as cache_admin_router
    app.include_router(cache_admin_router)
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..cache.cache_manager import get_cache_manager

router = APIRouter(prefix="/api/cache", tags=["Cache Admin"])


class CacheKey(BaseModel):
    """Cache key model"""
    key: str
    namespace: Optional[str] = ""


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    """
    Get cache statistics

    Returns detailed statistics about cache performance:
    - Memory cache: size, hits, misses, hit rate
    - Redis cache: availability and stats

    Returns:
        dict: Cache statistics
    """
    cache = get_cache_manager()
    return cache.get_stats()


@router.post("/clear")
async def clear_cache(namespace: Optional[str] = None):
    """
    Clear cache entries

    Clears all cache entries or entries in a specific namespace.

    Args:
        namespace: Optional namespace to clear (None = clear all)

    Returns:
        dict: Success message
    """
    cache = get_cache_manager()

    if namespace:
        cache.clear(namespace=namespace)
        return {
            "message": f"Cache cleared for namespace: {namespace}",
            "namespace": namespace
        }
    else:
        cache.clear()
        return {
            "message": "All cache entries cleared",
            "warning": "This affects all cached data across the application"
        }


@router.delete("/invalidate")
async def invalidate_cache_key(cache_key: CacheKey):
    """
    Invalidate specific cache key

    Removes a specific entry from the cache.

    Args:
        cache_key: Cache key to invalidate

    Returns:
        dict: Success message
    """
    cache = get_cache_manager()
    cache.delete(cache_key.key, namespace=cache_key.namespace)

    return {
        "message": "Cache key invalidated",
        "key": cache_key.key,
        "namespace": cache_key.namespace or "default"
    }


@router.get("/health")
async def cache_health():
    """
    Check cache health

    Returns cache availability and basic stats.

    Returns:
        dict: Cache health status
    """
    cache = get_cache_manager()
    stats = cache.get_stats()

    memory_stats = stats.get("memory_cache", {})
    redis_available = stats.get("redis_available", False)

    return {
        "status": "healthy",
        "memory_cache": {
            "available": True,
            "size": memory_stats.get("size", 0),
            "hit_rate": memory_stats.get("hit_rate", 0)
        },
        "redis_cache": {
            "available": redis_available
        }
    }

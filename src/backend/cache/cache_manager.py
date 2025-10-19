"""
Cache Manager

Implements multi-tier caching strategy:
- In-memory LRU cache for hot data
- Optional Redis for distributed caching
- Automatic cache invalidation
- Cache statistics and monitoring

Usage:
    from cache.cache_manager import get_cache_manager

    cache = get_cache_manager()

    # Cache data
    cache.set("key", value, ttl=300)

    # Retrieve data
    data = cache.get("key")

    # Cache decorator
    @cache.cached(ttl=300)
    def expensive_function():
        return result
"""

import time
import json
import hashlib
import pickle
from functools import wraps
from collections import OrderedDict
from typing import Any, Optional, Callable, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class LRUCache:
    """
    Least Recently Used (LRU) cache implementation

    Thread-safe in-memory cache with TTL support.
    Automatically evicts least recently used items when full.
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize LRU cache

        Args:
            max_size: Maximum number of items to cache
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.expiry_times: Dict[str, float] = {}

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.expiry_times:
            return True

        return time.time() > self.expiry_times[key]

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.misses += 1
            return None

        if self._is_expired(key):
            # Remove expired entry
            del self.cache[key]
            del self.expiry_times[key]
            self.misses += 1
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1

        return self.cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None uses default)
        """
        # Remove if exists (to update position)
        if key in self.cache:
            del self.cache[key]

        # Evict oldest if full
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.expiry_times[oldest_key]
            self.evictions += 1

        # Add new entry
        self.cache[key] = value
        ttl = ttl if ttl is not None else self.default_ttl
        self.expiry_times[key] = time.time() + ttl

    def delete(self, key: str):
        """Delete entry from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.expiry_times[key]

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.expiry_times.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }


class RedisCache:
    """
    Redis-based distributed cache

    Optional Redis backend for multi-instance deployments.
    Falls back to in-memory cache if Redis is unavailable.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 300):
        """
        Initialize Redis cache

        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.available = False

        try:
            import redis
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info(f"Redis cache connected: {redis_url}")
        except ImportError:
            logger.warning("Redis not installed. Install with: pip install redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.available:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in Redis cache"""
        if not self.available:
            return

        try:
            ttl = ttl if ttl is not None else self.default_ttl
            serialized = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def delete(self, key: str):
        """Delete entry from Redis cache"""
        if not self.available:
            return

        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    def clear(self):
        """Clear all cache entries (use with caution!)"""
        if not self.available:
            return

        try:
            self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")


class CacheManager:
    """
    Multi-tier cache manager

    Combines in-memory LRU cache with optional Redis backend.
    Provides automatic cache invalidation and statistics.
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 300,
        redis_url: Optional[str] = None,
        enable_redis: bool = False
    ):
        """
        Initialize cache manager

        Args:
            max_size: Max size of in-memory cache
            default_ttl: Default TTL in seconds
            redis_url: Redis connection URL (optional)
            enable_redis: Whether to use Redis
        """
        # In-memory cache (always available)
        self.memory_cache = LRUCache(max_size=max_size, default_ttl=default_ttl)

        # Redis cache (optional)
        self.redis_cache = None
        if enable_redis and redis_url:
            self.redis_cache = RedisCache(redis_url=redis_url, default_ttl=default_ttl)

    def _make_key(self, key: str, namespace: str = "") -> str:
        """Create namespaced cache key"""
        if namespace:
            return f"{namespace}:{key}"
        return key

    def get(self, key: str, namespace: str = "") -> Optional[Any]:
        """
        Get value from cache

        Tries Redis first (if available), then in-memory cache.

        Args:
            key: Cache key
            namespace: Optional namespace for key isolation

        Returns:
            Cached value or None
        """
        full_key = self._make_key(key, namespace)

        # Try Redis first
        if self.redis_cache and self.redis_cache.available:
            value = self.redis_cache.get(full_key)
            if value is not None:
                # Also cache in memory for faster subsequent access
                self.memory_cache.set(full_key, value)
                return value

        # Fallback to in-memory cache
        return self.memory_cache.get(full_key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = ""):
        """
        Set value in cache

        Stores in both Redis and in-memory cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            namespace: Optional namespace
        """
        full_key = self._make_key(key, namespace)

        # Store in Redis
        if self.redis_cache and self.redis_cache.available:
            self.redis_cache.set(full_key, value, ttl)

        # Store in memory
        self.memory_cache.set(full_key, value, ttl)

    def delete(self, key: str, namespace: str = ""):
        """Delete entry from all cache tiers"""
        full_key = self._make_key(key, namespace)

        if self.redis_cache and self.redis_cache.available:
            self.redis_cache.delete(full_key)

        self.memory_cache.delete(full_key)

    def clear(self, namespace: str = ""):
        """
        Clear cache entries

        If namespace is provided, only clears that namespace.
        Otherwise, clears all entries.
        """
        if namespace:
            # Clear specific namespace (in-memory only for now)
            # Redis pattern deletion would require scanning
            keys_to_delete = [
                k for k in self.memory_cache.cache.keys()
                if k.startswith(f"{namespace}:")
            ]
            for key in keys_to_delete:
                self.memory_cache.delete(key)
        else:
            # Clear all
            self.memory_cache.clear()
            if self.redis_cache and self.redis_cache.available:
                self.redis_cache.clear()

    def cached(
        self,
        ttl: Optional[int] = None,
        namespace: str = "",
        key_func: Optional[Callable] = None
    ):
        """
        Decorator to cache function results

        Args:
            ttl: Cache TTL in seconds
            namespace: Cache namespace
            key_func: Function to generate cache key from args

        Usage:
            @cache.cached(ttl=300, namespace="glossary")
            def get_entry(id: int):
                return expensive_query(id)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default: hash function name + args
                    key_parts = [func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    key_string = ":".join(key_parts)
                    cache_key = hashlib.md5(key_string.encode()).hexdigest()

                # Try to get from cache
                cached_value = self.get(cache_key, namespace=namespace)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value

                # Execute function
                logger.debug(f"Cache miss: {cache_key}")
                result = func(*args, **kwargs)

                # Store in cache
                self.set(cache_key, result, ttl=ttl, namespace=namespace)

                return result

            return wrapper
        return decorator

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "memory_cache": self.memory_cache.get_stats(),
            "redis_available": self.redis_cache.available if self.redis_cache else False
        }

        # Add Redis stats if available
        if self.redis_cache and self.redis_cache.available:
            try:
                info = self.redis_cache.redis_client.info("stats")
                stats["redis_stats"] = {
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                    "keys": self.redis_cache.redis_client.dbsize()
                }
            except Exception:
                pass

        return stats


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(
    max_size: int = 1000,
    default_ttl: int = 300,
    redis_url: Optional[str] = None,
    enable_redis: bool = False
) -> CacheManager:
    """
    Get or create global cache manager

    Args:
        max_size: Max cache size
        default_ttl: Default TTL
        redis_url: Redis URL
        enable_redis: Enable Redis

    Returns:
        CacheManager instance
    """
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager(
            max_size=max_size,
            default_ttl=default_ttl,
            redis_url=redis_url,
            enable_redis=enable_redis
        )

    return _cache_manager


def init_cache_from_settings(settings):
    """
    Initialize cache from application settings

    Args:
        settings: Application settings instance
    """
    return get_cache_manager(
        max_size=settings.CACHE_MAX_SIZE,
        default_ttl=settings.CACHE_TTL,
        redis_url=getattr(settings, 'REDIS_URL', None),
        enable_redis=settings.CACHE_ENABLED and getattr(settings, 'REDIS_ENABLED', False)
    )

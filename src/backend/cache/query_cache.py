"""
Query Result Caching

Provides caching for database query results.
Automatically invalidates cache on data changes.

Usage:
    from cache.query_cache import QueryCache

    query_cache = QueryCache()

    # Cache query result
    @query_cache.cached_query(ttl=300)
    def get_glossary_entries(limit=100):
        return session.query(GlossaryEntry).limit(limit).all()

    # Invalidate on update
    query_cache.invalidate_glossary_entry(entry_id)
"""

from typing import List, Optional, Callable, Any
from functools import wraps
import logging

from .cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


class QueryCache:
    """
    Database query result caching

    Caches expensive database queries with automatic invalidation.
    """

    # Cache namespaces
    NAMESPACE_GLOSSARY = "glossary"
    NAMESPACE_SEARCH = "search"
    NAMESPACE_RELATIONSHIPS = "relationships"
    NAMESPACE_STATS = "stats"

    def __init__(self):
        """Initialize query cache"""
        self.cache = get_cache_manager()

    def cached_query(
        self,
        ttl: int = 300,
        namespace: str = "",
        key_prefix: str = ""
    ):
        """
        Decorator to cache query results

        Args:
            ttl: Cache TTL in seconds
            namespace: Cache namespace
            key_prefix: Prefix for cache key

        Usage:
            @query_cache.cached_query(ttl=300, namespace="glossary")
            def get_entries(limit=100):
                return query_database()
        """
        return self.cache.cached(ttl=ttl, namespace=namespace)

    # Glossary entry caching
    def get_entry_by_id(self, entry_id: int) -> Optional[Any]:
        """Get cached entry by ID"""
        return self.cache.get(f"entry:{entry_id}", namespace=self.NAMESPACE_GLOSSARY)

    def set_entry(self, entry_id: int, entry_data: Any, ttl: int = 300):
        """Cache entry by ID"""
        self.cache.set(f"entry:{entry_id}", entry_data, ttl=ttl, namespace=self.NAMESPACE_GLOSSARY)

    def invalidate_glossary_entry(self, entry_id: int):
        """Invalidate cached entry"""
        logger.info(f"Invalidating cache for entry: {entry_id}")
        self.cache.delete(f"entry:{entry_id}", namespace=self.NAMESPACE_GLOSSARY)

        # Also invalidate list caches
        self.invalidate_glossary_lists()

    def invalidate_glossary_lists(self):
        """Invalidate all glossary list caches"""
        logger.info("Invalidating glossary list caches")
        self.cache.clear(namespace=self.NAMESPACE_GLOSSARY)

    # Search result caching
    def get_search_results(self, query_hash: str) -> Optional[Any]:
        """Get cached search results"""
        return self.cache.get(f"search:{query_hash}", namespace=self.NAMESPACE_SEARCH)

    def set_search_results(self, query_hash: str, results: Any, ttl: int = 300):
        """Cache search results"""
        self.cache.set(f"search:{query_hash}", results, ttl=ttl, namespace=self.NAMESPACE_SEARCH)

    def invalidate_search_cache(self):
        """Invalidate all search caches"""
        logger.info("Invalidating search cache")
        self.cache.clear(namespace=self.NAMESPACE_SEARCH)

    # Relationship caching
    def get_relationships(self, entry_id: int) -> Optional[Any]:
        """Get cached relationships"""
        return self.cache.get(f"relationships:{entry_id}", namespace=self.NAMESPACE_RELATIONSHIPS)

    def set_relationships(self, entry_id: int, relationships: Any, ttl: int = 600):
        """Cache relationships (longer TTL)"""
        self.cache.set(
            f"relationships:{entry_id}",
            relationships,
            ttl=ttl,
            namespace=self.NAMESPACE_RELATIONSHIPS
        )

    def invalidate_relationships(self, entry_id: Optional[int] = None):
        """Invalidate relationship caches"""
        if entry_id:
            logger.info(f"Invalidating relationships for entry: {entry_id}")
            self.cache.delete(f"relationships:{entry_id}", namespace=self.NAMESPACE_RELATIONSHIPS)
        else:
            logger.info("Invalidating all relationship caches")
            self.cache.clear(namespace=self.NAMESPACE_RELATIONSHIPS)

    # Statistics caching
    def get_stats(self, stat_type: str) -> Optional[Any]:
        """Get cached statistics"""
        return self.cache.get(f"stats:{stat_type}", namespace=self.NAMESPACE_STATS)

    def set_stats(self, stat_type: str, stats_data: Any, ttl: int = 600):
        """Cache statistics (longer TTL - stats change infrequently)"""
        self.cache.set(f"stats:{stat_type}", stats_data, ttl=ttl, namespace=self.NAMESPACE_STATS)

    def invalidate_stats(self):
        """Invalidate statistics cache"""
        logger.info("Invalidating statistics cache")
        self.cache.clear(namespace=self.NAMESPACE_STATS)

    # Global invalidation
    def invalidate_all(self):
        """Invalidate all caches"""
        logger.warning("Invalidating ALL caches")
        self.cache.clear()

    def get_cache_stats(self) -> dict:
        """Get cache performance statistics"""
        return self.cache.get_stats()


# Global query cache instance
_query_cache: Optional[QueryCache] = None


def get_query_cache() -> QueryCache:
    """Get or create global query cache"""
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCache()
    return _query_cache


def invalidate_on_change(entity_type: str = "glossary"):
    """
    Decorator to invalidate cache on data changes

    Usage:
        @invalidate_on_change(entity_type="glossary")
        def update_entry(entry_id, data):
            # Update database
            return updated_entry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)

            # Invalidate relevant caches
            cache = get_query_cache()

            if entity_type == "glossary":
                # Get entry_id from args if available
                entry_id = kwargs.get('entry_id') or (args[0] if args else None)
                if entry_id:
                    cache.invalidate_glossary_entry(entry_id)
                else:
                    cache.invalidate_glossary_lists()

                # Also invalidate search (entries changed)
                cache.invalidate_search_cache()
                cache.invalidate_stats()

            elif entity_type == "relationship":
                cache.invalidate_relationships()
                cache.invalidate_stats()

            elif entity_type == "all":
                cache.invalidate_all()

            return result

        return wrapper
    return decorator

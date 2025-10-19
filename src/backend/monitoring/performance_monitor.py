"""
Advanced Performance Monitoring

Tracks detailed performance metrics:
- Database query performance
- Cache hit/miss rates
- API endpoint latency
- Memory usage patterns
- Slow query detection

Usage:
    from monitoring.performance_monitor import get_performance_monitor

    perf = get_performance_monitor()
    perf.track_query(query_name, duration_ms)
"""

import time
import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Advanced performance monitoring

    Tracks and analyzes application performance metrics.
    """

    def __init__(
        self,
        slow_query_threshold_ms: float = 1000.0,
        slow_api_threshold_ms: float = 500.0,
        history_size: int = 1000
    ):
        """
        Initialize performance monitor

        Args:
            slow_query_threshold_ms: Threshold for slow database queries
            slow_api_threshold_ms: Threshold for slow API responses
            history_size: Number of recent metrics to keep
        """
        self.slow_query_threshold = slow_query_threshold_ms
        self.slow_api_threshold = slow_api_threshold_ms
        self.history_size = history_size

        # Query performance tracking
        self.query_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.query_counts: Dict[str, int] = defaultdict(int)
        self.slow_queries: deque = deque(maxlen=100)  # Last 100 slow queries

        # API endpoint performance
        self.endpoint_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.endpoint_counts: Dict[str, int] = defaultdict(int)
        self.slow_endpoints: deque = deque(maxlen=100)

        # Cache performance
        self.cache_hits = 0
        self.cache_misses = 0

        # Memory tracking
        self.memory_samples: deque = deque(maxlen=history_size)

        # Start time
        self.start_time = datetime.utcnow()

    # ========================================
    # Query Performance Tracking
    # ========================================

    def track_query(self, query_name: str, duration_ms: float):
        """
        Track database query performance

        Args:
            query_name: Name/identifier of the query
            duration_ms: Query duration in milliseconds
        """
        self.query_times[query_name].append(duration_ms)
        self.query_counts[query_name] += 1

        # Log slow queries
        if duration_ms > self.slow_query_threshold:
            self.slow_queries.append({
                "query": query_name,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat()
            })

            logger.warning(
                f"Slow query detected: {query_name}",
                extra={
                    "query": query_name,
                    "duration_ms": duration_ms,
                    "threshold_ms": self.slow_query_threshold
                }
            )

    def get_query_stats(self, query_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get query performance statistics

        Args:
            query_name: Specific query name (None = all queries)

        Returns:
            dict: Query statistics
        """
        if query_name:
            times = list(self.query_times[query_name])
            if not times:
                return {"error": f"No data for query: {query_name}"}

            return {
                "query": query_name,
                "count": self.query_counts[query_name],
                "avg_ms": round(statistics.mean(times), 2),
                "median_ms": round(statistics.median(times), 2),
                "min_ms": round(min(times), 2),
                "max_ms": round(max(times), 2),
                "p95_ms": round(statistics.quantiles(times, n=20)[18], 2) if len(times) > 1 else round(times[0], 2),
                "p99_ms": round(statistics.quantiles(times, n=100)[98], 2) if len(times) > 1 else round(times[0], 2)
            }

        # All queries summary
        all_stats = {}
        for query_name in self.query_times.keys():
            all_stats[query_name] = self.get_query_stats(query_name)

        return all_stats

    # ========================================
    # API Endpoint Performance
    # ========================================

    def track_endpoint(self, endpoint: str, method: str, duration_ms: float, status_code: int):
        """
        Track API endpoint performance

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
        """
        key = f"{method} {endpoint}"

        self.endpoint_times[key].append(duration_ms)
        self.endpoint_counts[key] += 1

        # Log slow endpoints
        if duration_ms > self.slow_api_threshold:
            self.slow_endpoints.append({
                "endpoint": endpoint,
                "method": method,
                "duration_ms": duration_ms,
                "status_code": status_code,
                "timestamp": datetime.utcnow().isoformat()
            })

            logger.warning(
                f"Slow API endpoint: {key}",
                extra={
                    "endpoint": endpoint,
                    "method": method,
                    "duration_ms": duration_ms,
                    "status_code": status_code,
                    "threshold_ms": self.slow_api_threshold
                }
            )

    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get endpoint performance statistics

        Args:
            endpoint: Specific endpoint (None = all endpoints)

        Returns:
            dict: Endpoint statistics
        """
        if endpoint:
            times = list(self.endpoint_times[endpoint])
            if not times:
                return {"error": f"No data for endpoint: {endpoint}"}

            return {
                "endpoint": endpoint,
                "count": self.endpoint_counts[endpoint],
                "avg_ms": round(statistics.mean(times), 2),
                "median_ms": round(statistics.median(times), 2),
                "min_ms": round(min(times), 2),
                "max_ms": round(max(times), 2),
                "p95_ms": round(statistics.quantiles(times, n=20)[18], 2) if len(times) > 1 else round(times[0], 2),
                "p99_ms": round(statistics.quantiles(times, n=100)[98], 2) if len(times) > 1 else round(times[0], 2)
            }

        # All endpoints summary
        all_stats = {}
        for endpoint_key in self.endpoint_times.keys():
            all_stats[endpoint_key] = self.get_endpoint_stats(endpoint_key)

        return all_stats

    # ========================================
    # Cache Performance
    # ========================================

    def track_cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1

    def track_cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics

        Returns:
            dict: Cache statistics
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "miss_rate_percent": round(100 - hit_rate, 2)
        }

    # ========================================
    # Memory Tracking
    # ========================================

    def track_memory(self):
        """Sample current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()

            self.memory_samples.append({
                "timestamp": datetime.utcnow().isoformat(),
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
                "vms_mb": memory_info.vms / 1024 / 1024   # Virtual Memory Size
            })
        except ImportError:
            pass  # psutil not available

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics

        Returns:
            dict: Memory statistics
        """
        if not self.memory_samples:
            return {"error": "No memory samples available"}

        rss_values = [s["rss_mb"] for s in self.memory_samples]
        vms_values = [s["vms_mb"] for s in self.memory_samples]

        return {
            "rss": {
                "current_mb": round(rss_values[-1], 2),
                "avg_mb": round(statistics.mean(rss_values), 2),
                "max_mb": round(max(rss_values), 2),
                "min_mb": round(min(rss_values), 2)
            },
            "vms": {
                "current_mb": round(vms_values[-1], 2),
                "avg_mb": round(statistics.mean(vms_values), 2),
                "max_mb": round(max(vms_values), 2),
                "min_mb": round(min(vms_values), 2)
            },
            "samples": len(self.memory_samples)
        }

    # ========================================
    # Slow Operations
    # ========================================

    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent slow queries

        Args:
            limit: Number of slow queries to return

        Returns:
            list: Recent slow queries
        """
        return list(self.slow_queries)[-limit:]

    def get_slow_endpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent slow endpoints

        Args:
            limit: Number of slow endpoints to return

        Returns:
            list: Recent slow endpoints
        """
        return list(self.slow_endpoints)[-limit:]

    # ========================================
    # Comprehensive Stats
    # ========================================

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Get all performance statistics

        Returns:
            dict: Complete performance metrics
        """
        uptime = datetime.utcnow() - self.start_time

        return {
            "uptime": {
                "seconds": int(uptime.total_seconds()),
                "human_readable": str(uptime).split('.')[0]  # Remove microseconds
            },
            "queries": {
                "total_queries": sum(self.query_counts.values()),
                "unique_queries": len(self.query_counts),
                "slow_queries_count": len(self.slow_queries),
                "top_queries": self._get_top_queries(5)
            },
            "endpoints": {
                "total_requests": sum(self.endpoint_counts.values()),
                "unique_endpoints": len(self.endpoint_counts),
                "slow_endpoints_count": len(self.slow_endpoints),
                "top_endpoints": self._get_top_endpoints(5)
            },
            "cache": self.get_cache_stats(),
            "memory": self.get_memory_stats()
        }

    def _get_top_queries(self, limit: int) -> List[Dict[str, Any]]:
        """Get most frequently executed queries"""
        sorted_queries = sorted(
            self.query_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {
                "query": query,
                "count": count,
                "avg_ms": round(statistics.mean(self.query_times[query]), 2) if self.query_times[query] else 0
            }
            for query, count in sorted_queries
        ]

    def _get_top_endpoints(self, limit: int) -> List[Dict[str, Any]]:
        """Get most frequently accessed endpoints"""
        sorted_endpoints = sorted(
            self.endpoint_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {
                "endpoint": endpoint,
                "count": count,
                "avg_ms": round(statistics.mean(self.endpoint_times[endpoint]), 2) if self.endpoint_times[endpoint] else 0
            }
            for endpoint, count in sorted_endpoints
        ]

    # ========================================
    # Reset
    # ========================================

    def reset(self):
        """Reset all performance metrics"""
        self.query_times.clear()
        self.query_counts.clear()
        self.slow_queries.clear()

        self.endpoint_times.clear()
        self.endpoint_counts.clear()
        self.slow_endpoints.clear()

        self.cache_hits = 0
        self.cache_misses = 0

        self.memory_samples.clear()

        self.start_time = datetime.utcnow()

        logger.info("Performance metrics reset")


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor(
    slow_query_threshold_ms: float = 1000.0,
    slow_api_threshold_ms: float = 500.0
) -> PerformanceMonitor:
    """
    Get or create global performance monitor

    Args:
        slow_query_threshold_ms: Threshold for slow queries
        slow_api_threshold_ms: Threshold for slow API responses

    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor

    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor(
            slow_query_threshold_ms=slow_query_threshold_ms,
            slow_api_threshold_ms=slow_api_threshold_ms
        )

    return _performance_monitor

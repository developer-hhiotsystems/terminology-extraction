"""
Performance Tracking Middleware

Tracks request/response times for health monitoring.
Integrates with the health check system to provide performance metrics.

Usage:
    from middleware.performance_tracker import PerformanceTrackerMiddleware

    app.add_middleware(PerformanceTrackerMiddleware)
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from ..monitoring.health_check import get_health_checker


class PerformanceTrackerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track API request/response times

    Records request duration and feeds it to the health checker
    for performance monitoring.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track timing

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response: HTTP response with timing header
        """
        # Skip health check endpoints to avoid circular tracking
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record in health checker
        try:
            checker = get_health_checker()
            checker.record_request_time(duration)
        except Exception:
            # Don't fail request if tracking fails
            pass

        # Add timing header to response
        response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"

        return response

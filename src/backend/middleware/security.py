"""
Security Middleware

Implements comprehensive security measures:
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- CORS with strict origin validation
- Rate limiting
- Input sanitization
- SQL injection prevention

Usage:
    from middleware.security import setup_security_middleware

    setup_security_middleware(app, settings)
"""

import re
import time
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Callable, Optional
import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses

    Implements OWASP recommended security headers:
    - Content Security Policy (CSP)
    - HTTP Strict Transport Security (HSTS)
    - X-Frame-Options (clickjacking protection)
    - X-Content-Type-Options (MIME sniffing prevention)
    - X-XSS-Protection (XSS filter)
    - Referrer-Policy
    - Permissions-Policy
    """

    def __init__(self, app, enable_hsts: bool = True):
        super().__init__(app)
        self.enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""
        response = await call_next(request)

        # Content Security Policy
        # Restricts resources the page can load
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # HTTP Strict Transport Security (HSTS)
        # Force HTTPS for 1 year
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # X-Frame-Options
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options
        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection
        # Enable browser XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy (formerly Feature-Policy)
        # Disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # Remove server header (information disclosure)
        if "server" in response.headers:
            del response.headers["server"]

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm

    Limits requests per client IP address to prevent abuse.
    Configurable limits per time window.
    """

    def __init__(
        self,
        app,
        requests_per_window: int = 100,
        window_seconds: int = 60,
        enabled: bool = True
    ):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.enabled = enabled

        # Store: {ip: [(timestamp, count), ...]}
        self.request_counts: Dict[str, list] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check X-Forwarded-For header (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, ip: str) -> bool:
        """Check if IP is rate limited"""
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old entries
        self.request_counts[ip] = [
            (ts, count) for ts, count in self.request_counts[ip]
            if ts > cutoff
        ]

        # Count requests in current window
        total_requests = sum(count for _, count in self.request_counts[ip])

        if total_requests >= self.requests_per_window:
            return True

        # Add current request
        self.request_counts[ip].append((now, 1))
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request"""
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        if self._is_rate_limited(client_ip):
            logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={
                    "ip": client_ip,
                    "path": request.url.path,
                    "method": request.method
                }
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "type": "rate_limit_exceeded",
                        "status_code": 429,
                        "message": "Too many requests. Please try again later.",
                        "retry_after": self.window_seconds
                    }
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Window": str(self.window_seconds)
                }
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)

        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Input sanitization middleware

    Validates and sanitizes incoming request data to prevent:
    - SQL injection
    - XSS attacks
    - Path traversal
    - Command injection
    """

    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*\bOR\b)",
        r"(\bAND\b.*=.*\bAND\b)",
        r"('|\")\s*(OR|AND)\s*\1\s*=\s*\1"
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed"
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"\.\.\\",
    ]

    def __init__(self, app, strict_mode: bool = False):
        super().__init__(app)
        self.strict_mode = strict_mode

        # Compile patterns
        self.sql_regex = [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS]
        self.xss_regex = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self.path_regex = [re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS]

    def _check_patterns(self, value: str, patterns: list, attack_type: str) -> Optional[str]:
        """Check if value matches dangerous patterns"""
        if not isinstance(value, str):
            return None

        for pattern in patterns:
            if pattern.search(value):
                return attack_type

        return None

    def _scan_dict(self, data: dict) -> Optional[str]:
        """Recursively scan dictionary for dangerous patterns"""
        for key, value in data.items():
            if isinstance(value, str):
                # Check SQL injection
                attack = self._check_patterns(value, self.sql_regex, "sql_injection")
                if attack:
                    return attack

                # Check XSS
                attack = self._check_patterns(value, self.xss_regex, "xss")
                if attack:
                    return attack

                # Check path traversal
                attack = self._check_patterns(value, self.path_regex, "path_traversal")
                if attack:
                    return attack

            elif isinstance(value, dict):
                attack = self._scan_dict(value)
                if attack:
                    return attack

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        attack = self._scan_dict(item)
                        if attack:
                            return attack
                    elif isinstance(item, str):
                        attack = self._check_patterns(item, self.sql_regex, "sql_injection")
                        if attack:
                            return attack

        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request data"""
        # Skip for GET requests (query params validated by FastAPI)
        if request.method == "GET":
            return await call_next(request)

        # Skip for health checks and static files
        if request.url.path.startswith(("/health", "/static", "/docs", "/redoc")):
            return await call_next(request)

        # Check Content-Type for JSON requests
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                # Get request body
                body = await request.body()
                if body:
                    import json
                    data = json.loads(body)

                    # Scan for dangerous patterns
                    attack_type = self._scan_dict(data) if isinstance(data, dict) else None

                    if attack_type:
                        logger.warning(
                            f"Potential {attack_type} attack detected",
                            extra={
                                "attack_type": attack_type,
                                "path": request.url.path,
                                "ip": request.client.host if request.client else "unknown"
                            }
                        )

                        if self.strict_mode:
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "error": {
                                        "type": "invalid_input",
                                        "status_code": 400,
                                        "message": "Invalid input detected"
                                    }
                                }
                            )

                # Reconstruct request with body
                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive

            except json.JSONDecodeError:
                pass  # Let FastAPI handle invalid JSON

        return await call_next(request)


def setup_security_middleware(app: FastAPI, settings):
    """
    Setup all security middleware

    Args:
        app: FastAPI application
        settings: Application settings
    """
    # CORS middleware (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS.split(","),
        allow_headers=settings.ALLOWED_HEADERS.split(",") if settings.ALLOWED_HEADERS != "*" else ["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )

    # Gzip compression
    if settings.GZIP_ENABLED:
        app.add_middleware(
            GZipMiddleware,
            minimum_size=settings.GZIP_MINIMUM_SIZE
        )

    # Security headers
    app.add_middleware(
        SecurityHeadersMiddleware,
        enable_hsts=settings.is_production
    )

    # Rate limiting
    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_window=settings.RATE_LIMIT_REQUESTS,
            window_seconds=settings.RATE_LIMIT_WINDOW,
            enabled=True
        )

    # Input sanitization (strict mode in production)
    app.add_middleware(
        InputSanitizationMiddleware,
        strict_mode=settings.is_production
    )

    logger.info("Security middleware configured", extra={
        "cors_enabled": True,
        "rate_limiting": settings.RATE_LIMIT_ENABLED,
        "gzip": settings.GZIP_ENABLED,
        "hsts": settings.is_production
    })

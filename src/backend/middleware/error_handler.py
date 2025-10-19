"""
Global Error Handler Middleware

Catches all unhandled exceptions and returns consistent error responses.
Integrates with logging and error tracking.

Usage:
    from middleware.error_handler import setup_error_handlers

    setup_error_handlers(app)
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Callable


logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions

    Returns consistent error response for HTTP errors (404, 403, etc.)
    """
    logger.warning(
        f"HTTP {exc.status_code} - {exc.detail}",
        extra={
            'status_code': exc.status_code,
            'path': request.url.path,
            'method': request.method
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "status_code": exc.status_code,
                "message": exc.detail,
                "path": request.url.path
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors

    Returns detailed validation error information
    """
    logger.warning(
        "Validation error",
        extra={
            'path': request.url.path,
            'method': request.method,
            'errors': exc.errors()
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "status_code": 422,
                "message": "Request validation failed",
                "path": request.url.path,
                "details": exc.errors()
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all other unhandled exceptions

    Logs the error and returns a generic 500 error response
    without exposing internal details.
    """
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={
            'path': request.url.path,
            'method': request.method,
            'exception_type': type(exc).__name__
        }
    )

    # In production, don't expose internal error details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "status_code": 500,
                "message": "An internal server error occurred",
                "path": request.url.path
            }
        }
    )


def setup_error_handlers(app: FastAPI):
    """
    Setup all error handlers for the FastAPI app

    Args:
        app: FastAPI application instance
    """
    # HTTP exceptions (404, 403, etc.)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Validation errors (422)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # All other exceptions (500)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers configured")

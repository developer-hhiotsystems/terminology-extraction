"""
Error Tracking and Logging

Provides structured logging and error tracking for production:
- Structured JSON logging
- Error classification and severity levels
- Optional Sentry integration
- Request context tracking
- Error rate monitoring

Usage:
    from monitoring.error_tracking import get_logger, setup_error_tracking

    logger = get_logger(__name__)
    logger.info("User action", extra={"user_id": 123, "action": "search"})
    logger.error("Database error", exc_info=True)
"""

import os
import sys
import logging
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging

    Outputs log records as JSON for easier parsing by log aggregation tools
    (ELK, Splunk, Datadog, etc.)
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add custom fields from extra parameter
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint

        return json.dumps(log_data)


class RequestContextFilter(logging.Filter):
    """
    Add request context to log records

    Adds request_id, user_id, endpoint to all log records
    when available in the context.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to record"""
        # These would be set by middleware
        # For now, just ensure attributes exist
        if not hasattr(record, 'request_id'):
            record.request_id = None
        if not hasattr(record, 'user_id'):
            record.user_id = None
        if not hasattr(record, 'endpoint'):
            record.endpoint = None

        return True


class ErrorRateTracker:
    """
    Track error rates for monitoring

    Maintains counters of errors by level and type
    for alerting and dashboards.
    """

    def __init__(self):
        self.error_counts = {
            'CRITICAL': 0,
            'ERROR': 0,
            'WARNING': 0,
            'INFO': 0,
            'DEBUG': 0
        }
        self.error_types: Dict[str, int] = {}
        self.start_time = datetime.utcnow()

    def record_error(self, level: str, error_type: Optional[str] = None):
        """Record an error occurrence"""
        if level in self.error_counts:
            self.error_counts[level] += 1

        if error_type:
            self.error_types[error_type] = self.error_types.get(error_type, 0) + 1

    def get_error_rate(self, level: str = 'ERROR') -> float:
        """
        Get error rate (errors per minute)

        Args:
            level: Log level to calculate rate for

        Returns:
            float: Errors per minute
        """
        elapsed_minutes = (datetime.utcnow() - self.start_time).total_seconds() / 60
        if elapsed_minutes < 1:
            elapsed_minutes = 1

        return self.error_counts.get(level, 0) / elapsed_minutes

    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        elapsed_minutes = (datetime.utcnow() - self.start_time).total_seconds() / 60
        if elapsed_minutes < 1:
            elapsed_minutes = 1

        return {
            "error_counts": self.error_counts,
            "error_types": self.error_types,
            "total_errors": sum(self.error_counts.values()),
            "error_rate_per_minute": sum(self.error_counts.values()) / elapsed_minutes,
            "tracking_duration_minutes": round(elapsed_minutes, 2),
            "start_time": self.start_time.isoformat()
        }

    def reset(self):
        """Reset all counters"""
        self.error_counts = {k: 0 for k in self.error_counts}
        self.error_types.clear()
        self.start_time = datetime.utcnow()


# Global error rate tracker
_error_tracker = ErrorRateTracker()


def get_error_tracker() -> ErrorRateTracker:
    """Get global error tracker instance"""
    return _error_tracker


class ErrorTrackingHandler(logging.Handler):
    """
    Custom handler that tracks error rates

    Records errors in the error tracker for monitoring
    """

    def emit(self, record: logging.LogRecord):
        """Handle log record"""
        try:
            tracker = get_error_tracker()
            tracker.record_error(
                level=record.levelname,
                error_type=record.exc_info[0].__name__ if record.exc_info else None
            )
        except Exception:
            # Don't fail logging if tracking fails
            pass


def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 10,
    json_format: bool = True,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup application logging

    Args:
        log_dir: Directory for log files
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep
        json_format: Use JSON format for log files
        console_output: Also log to console

    Returns:
        logging.Logger: Configured root logger
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # File handler with rotation (app.log)
    app_log_file = log_path / "app.log"
    file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))

    if json_format:
        file_handler.setFormatter(JSONFormatter())
    else:
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

    logger.addHandler(file_handler)

    # Error log file (errors.log) - only ERROR and CRITICAL
    error_log_file = log_path / "errors.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)

    if json_format:
        error_handler.setFormatter(JSONFormatter())
    else:
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
            'Location: %(pathname)s:%(lineno)d\n'
            '%(message)s\n'
        ))

    logger.addHandler(error_handler)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console_handler)

    # Add request context filter
    logger.addFilter(RequestContextFilter())

    # Add error tracking handler
    logger.addHandler(ErrorTrackingHandler())

    logger.info("Logging initialized", extra={
        'log_dir': str(log_path),
        'log_level': log_level,
        'json_format': json_format
    })

    return logger


def setup_sentry(dsn: Optional[str] = None, environment: str = "production") -> bool:
    """
    Setup Sentry error tracking (optional)

    Args:
        dsn: Sentry DSN (from environment or parameter)
        environment: Environment name (production, staging, development)

    Returns:
        bool: True if Sentry was initialized successfully
    """
    # Get DSN from parameter or environment
    sentry_dsn = dsn or os.getenv("SENTRY_DSN")

    if not sentry_dsn:
        logging.info("Sentry DSN not configured - skipping Sentry initialization")
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        # Setup Sentry logging integration
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )

        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            integrations=[
                sentry_logging,
                SqlalchemyIntegration(),
            ],
            # Don't send PII
            send_default_pii=False,
            # Release tracking
            release=os.getenv("APP_VERSION", "1.0.0"),
        )

        logging.info("Sentry error tracking initialized", extra={
            'environment': environment,
            'traces_sample_rate': 0.1
        })

        return True

    except ImportError:
        logging.warning(
            "Sentry SDK not installed - install with: pip install sentry-sdk"
        )
        return False
    except Exception as e:
        logging.error(f"Failed to initialize Sentry: {e}", exc_info=True)
        return False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def log_exception(
    logger: logging.Logger,
    message: str,
    exc_info: Any = True,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Log an exception with context

    Args:
        logger: Logger instance
        message: Error message
        exc_info: Exception info (True to auto-capture, or exception object)
        extra: Additional context data
    """
    if extra:
        # Store in extra_data attribute for JSONFormatter
        logger.error(message, exc_info=exc_info, extra={'extra_data': extra})
    else:
        logger.error(message, exc_info=exc_info)


def setup_error_tracking(
    log_level: str = "INFO",
    enable_sentry: bool = False,
    sentry_dsn: Optional[str] = None,
    environment: str = "production"
) -> logging.Logger:
    """
    Complete error tracking setup

    Sets up both logging and Sentry (if enabled)

    Args:
        log_level: Minimum log level
        enable_sentry: Whether to enable Sentry
        sentry_dsn: Sentry DSN (optional, can use SENTRY_DSN env var)
        environment: Environment name

    Returns:
        logging.Logger: Configured root logger
    """
    # Setup logging
    logger = setup_logging(log_level=log_level)

    # Setup Sentry if requested
    if enable_sentry:
        setup_sentry(dsn=sentry_dsn, environment=environment)

    return logger

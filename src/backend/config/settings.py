"""
Configuration Management

Loads and validates configuration from environment variables.
Supports multiple environments (development, staging, production).

Usage:
    from config.settings import get_settings

    settings = get_settings()
    print(settings.DATABASE_URL)
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables

    Uses pydantic for validation and type conversion.
    Values can be overridden with environment variables.
    """

    # ========================================
    # Application
    # ========================================
    APP_NAME: str = "Glossary App"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")

    # ========================================
    # Server
    # ========================================
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=9123, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")
    RELOAD: bool = Field(default=True, env="RELOAD")

    # ========================================
    # Database
    # ========================================
    DATABASE_URL: str = Field(
        default="sqlite:///data/glossary.db",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # ========================================
    # Logging
    # ========================================
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_DIR: str = Field(default="logs", env="LOG_DIR")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_MAX_BYTES: int = Field(default=10485760, env="LOG_MAX_BYTES")  # 10 MB
    LOG_BACKUP_COUNT: int = Field(default=10, env="LOG_BACKUP_COUNT")

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    # ========================================
    # Security
    # ========================================
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_METHODS: str = Field(
        default="GET,POST,PUT,DELETE,PATCH",
        env="ALLOWED_METHODS"
    )
    ALLOWED_HEADERS: str = Field(default="*", env="ALLOWED_HEADERS")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")

    @property
    def ALLOWED_ORIGINS_LIST(self) -> List[str]:
        """Convert ALLOWED_ORIGINS string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        """Ensure SECRET_KEY is changed in production"""
        env = values.get("ENVIRONMENT", "development")
        if env == "production" and v == "dev-secret-key-change-in-production":
            raise ValueError(
                "SECRET_KEY must be changed in production! "
                "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        return v

    # ========================================
    # Backup
    # ========================================
    BACKUP_ENABLED: bool = Field(default=True, env="BACKUP_ENABLED")
    BACKUP_DIR: str = Field(default="backups", env="BACKUP_DIR")
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    BACKUP_COMPRESS: bool = Field(default=True, env="BACKUP_COMPRESS")
    BACKUP_VERIFY: bool = Field(default=True, env="BACKUP_VERIFY")
    BACKUP_SCHEDULE: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")

    # ========================================
    # Health Monitoring
    # ========================================
    HEALTH_CHECK_ENABLED: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    DISK_WARNING_THRESHOLD_GB: float = Field(default=5.0, env="DISK_WARNING_THRESHOLD_GB")
    DISK_CRITICAL_THRESHOLD_GB: float = Field(default=1.0, env="DISK_CRITICAL_THRESHOLD_GB")
    MEMORY_WARNING_THRESHOLD_PERCENT: float = Field(default=85.0, env="MEMORY_WARNING_THRESHOLD_PERCENT")
    MEMORY_CRITICAL_THRESHOLD_PERCENT: float = Field(default=95.0, env="MEMORY_CRITICAL_THRESHOLD_PERCENT")

    # ========================================
    # Error Tracking (Sentry)
    # ========================================
    SENTRY_ENABLED: bool = Field(default=False, env="SENTRY_ENABLED")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, env="SENTRY_TRACES_SAMPLE_RATE")
    SENTRY_ENVIRONMENT: str = Field(default="development", env="SENTRY_ENVIRONMENT")

    # ========================================
    # NLP / spaCy
    # ========================================
    SPACY_MODEL: str = Field(default="en_core_web_sm", env="SPACY_MODEL")
    NLP_BATCH_SIZE: int = Field(default=100, env="NLP_BATCH_SIZE")
    NLP_MIN_CONFIDENCE: float = Field(default=0.5, env="NLP_MIN_CONFIDENCE")

    # ========================================
    # Full-Text Search (FTS5)
    # ========================================
    FTS_ENABLED: bool = Field(default=True, env="FTS_ENABLED")
    FTS_SNIPPET_LENGTH: int = Field(default=200, env="FTS_SNIPPET_LENGTH")
    FTS_MAX_RESULTS: int = Field(default=100, env="FTS_MAX_RESULTS")

    # ========================================
    # File Upload
    # ========================================
    UPLOAD_MAX_SIZE_MB: int = Field(default=50, env="UPLOAD_MAX_SIZE_MB")
    UPLOAD_ALLOWED_EXTENSIONS: str = Field(default=".pdf,.txt,.docx", env="UPLOAD_ALLOWED_EXTENSIONS")
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")

    @property
    def UPLOAD_ALLOWED_EXTENSIONS_LIST(self) -> List[str]:
        """Convert UPLOAD_ALLOWED_EXTENSIONS string to list"""
        return [ext.strip() for ext in self.UPLOAD_ALLOWED_EXTENSIONS.split(",")]

    # ========================================
    # Frontend
    # ========================================
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")

    # ========================================
    # Performance
    # ========================================
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    CONNECTION_POOL_SIZE: int = Field(default=20, env="CONNECTION_POOL_SIZE")
    CACHE_ENABLED: bool = Field(default=False, env="CACHE_ENABLED")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")
    CACHE_MAX_SIZE: int = Field(default=1000, env="CACHE_MAX_SIZE")

    # ========================================
    # Monitoring & Metrics
    # ========================================
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_PORT: int = Field(default=9124, env="METRICS_PORT")
    PROMETHEUS_ENABLED: bool = Field(default=False, env="PROMETHEUS_ENABLED")
    PROMETHEUS_ENDPOINT: str = Field(default="/metrics", env="PROMETHEUS_ENDPOINT")

    # ========================================
    # Email Notifications (Optional)
    # ========================================
    EMAIL_ENABLED: bool = Field(default=False, env="EMAIL_ENABLED")
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_FROM: str = Field(default="glossary-app@example.com", env="SMTP_FROM")
    SMTP_TO: str = Field(default="admin@example.com", env="SMTP_TO")

    # ========================================
    # Development Tools
    # ========================================
    AUTO_RELOAD: bool = Field(default=True, env="AUTO_RELOAD")
    SHOW_ERROR_DETAILS: bool = Field(default=True, env="SHOW_ERROR_DETAILS")
    DOCS_ENABLED: bool = Field(default=True, env="DOCS_ENABLED")
    DOCS_URL: str = Field(default="/docs", env="DOCS_URL")
    REDOC_URL: str = Field(default="/redoc", env="REDOC_URL")

    # ========================================
    # Production Optimizations
    # ========================================
    GZIP_ENABLED: bool = Field(default=True, env="GZIP_ENABLED")
    GZIP_MINIMUM_SIZE: int = Field(default=1000, env="GZIP_MINIMUM_SIZE")
    RESPONSE_CACHE_ENABLED: bool = Field(default=False, env="RESPONSE_CACHE_ENABLED")
    QUERY_LOGGING: bool = Field(default=False, env="QUERY_LOGGING")
    SLOW_QUERY_THRESHOLD_MS: int = Field(default=1000, env="SLOW_QUERY_THRESHOLD_MS")

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging"""
        return self.ENVIRONMENT == "staging"

    def to_dict(self) -> dict:
        """Convert settings to dictionary"""
        return self.dict()

    def print_config(self):
        """Print current configuration (excluding secrets)"""
        config = self.dict()

        # Redact sensitive fields
        sensitive_fields = [
            "SECRET_KEY", "SENTRY_DSN", "SMTP_PASSWORD", "SMTP_USER"
        ]

        for field in sensitive_fields:
            if field in config and config[field]:
                config[field] = "***REDACTED***"

        print("=" * 80)
        print("CURRENT CONFIGURATION")
        print("=" * 80)

        for key, value in sorted(config.items()):
            print(f"{key}: {value}")

        print("=" * 80)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance

    Uses lru_cache to ensure settings are loaded once
    and reused throughout the application.

    Returns:
        Settings: Application settings
    """
    return Settings()


def validate_production_config(settings: Settings):
    """
    Validate production configuration

    Raises ValueError if production config is invalid

    Args:
        settings: Settings instance to validate
    """
    if not settings.is_production:
        return

    errors = []

    # Check SECRET_KEY
    if settings.SECRET_KEY == "dev-secret-key-change-in-production":
        errors.append("SECRET_KEY must be changed in production")

    # Check DEBUG is disabled
    if settings.DEBUG:
        errors.append("DEBUG must be False in production")

    # Check RELOAD is disabled
    if settings.RELOAD:
        errors.append("RELOAD must be False in production")

    # Check DOCS are disabled
    if settings.DOCS_ENABLED:
        errors.append("API docs should be disabled in production (DOCS_ENABLED=false)")

    # Check backups are enabled
    if not settings.BACKUP_ENABLED:
        errors.append("Backups should be enabled in production (BACKUP_ENABLED=true)")

    # Check health checks are enabled
    if not settings.HEALTH_CHECK_ENABLED:
        errors.append("Health checks should be enabled in production")

    # Check error tracking
    if not settings.SENTRY_ENABLED:
        print("WARNING: Sentry error tracking is not enabled in production")

    # Check CORS
    if "*" in settings.ALLOWED_ORIGINS:
        errors.append("ALLOWED_ORIGINS should not use wildcard (*) in production")

    if errors:
        raise ValueError(
            "Production configuration validation failed:\n" +
            "\n".join(f"  - {error}" for error in errors)
        )

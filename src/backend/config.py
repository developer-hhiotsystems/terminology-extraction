"""
Configuration management for the Glossary API
"""
import os
from dotenv import load_dotenv
from src.backend.constants import (
    DATABASE_URL_SQLITE,
    DATABASE_URL_POSTGRESQL,
    DB_TYPE_SQLITE,
    DB_TYPE_POSTGRESQL,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_POOL_SIZE,
    POSTGRES_MAX_OVERFLOW,
    POSTGRES_POOL_TIMEOUT,
    POSTGRES_POOL_RECYCLE
)

load_dotenv()

class Config:
    """Application configuration"""

    # Database Type (sqlite or postgresql)
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", DB_TYPE_SQLITE)

    # Database URL - Auto-construct from environment or use provided URL
    DATABASE_URL = os.getenv("DATABASE_URL")

    # If DATABASE_URL not provided, construct it based on DATABASE_TYPE
    if not DATABASE_URL:
        if DATABASE_TYPE == DB_TYPE_POSTGRESQL:
            # Construct PostgreSQL URL from individual components
            _pg_host = os.getenv("POSTGRES_HOST", POSTGRES_HOST)
            _pg_port = os.getenv("POSTGRES_PORT", str(POSTGRES_PORT))
            _pg_db = os.getenv("POSTGRES_DB", POSTGRES_DB)
            _pg_user = os.getenv("POSTGRES_USER", POSTGRES_USER)
            _pg_password = os.getenv("POSTGRES_PASSWORD", POSTGRES_PASSWORD)
            DATABASE_URL = f"postgresql://{_pg_user}:{_pg_password}@{_pg_host}:{_pg_port}/{_pg_db}"
        else:
            # Default to SQLite
            DATABASE_URL = os.getenv("SQLITE_DATABASE_URL", DATABASE_URL_SQLITE)

    # PostgreSQL connection pool settings
    POSTGRES_POOL_SIZE = int(os.getenv("POSTGRES_POOL_SIZE", POSTGRES_POOL_SIZE))
    POSTGRES_MAX_OVERFLOW = int(os.getenv("POSTGRES_MAX_OVERFLOW", POSTGRES_MAX_OVERFLOW))
    POSTGRES_POOL_TIMEOUT = int(os.getenv("POSTGRES_POOL_TIMEOUT", POSTGRES_POOL_TIMEOUT))
    POSTGRES_POOL_RECYCLE = int(os.getenv("POSTGRES_POOL_RECYCLE", POSTGRES_POOL_RECYCLE))

    # Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")  # Must be set in .env file

    # DeepL
    DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")

    # IATE
    IATE_DATASET_PATH = os.getenv("IATE_DATASET_PATH", "./data/iate/IATE_export.tbx")

    # File Upload
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))

    # Backup
    SQLITE_BACKUP_DIR = os.getenv("SQLITE_BACKUP_DIR", "./backups/sqlite")
    NEO4J_BACKUP_DIR = os.getenv("NEO4J_BACKUP_DIR", "./backups/neo4j")
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", 30))

    # Server
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Development
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # Default to False for security
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Migration
    ENABLE_MIGRATIONS = os.getenv("ENABLE_MIGRATIONS", "True").lower() == "true"

    @classmethod
    def is_postgresql(cls) -> bool:
        """Check if using PostgreSQL database"""
        return cls.DATABASE_TYPE == DB_TYPE_POSTGRESQL or "postgresql" in cls.DATABASE_URL.lower()

    @classmethod
    def is_sqlite(cls) -> bool:
        """Check if using SQLite database"""
        return cls.DATABASE_TYPE == DB_TYPE_SQLITE or "sqlite" in cls.DATABASE_URL.lower()

    @classmethod
    def get_database_info(cls) -> dict:
        """Get database configuration info"""
        return {
            "type": cls.DATABASE_TYPE,
            "url": cls.DATABASE_URL.replace(cls.DATABASE_URL.split("@")[0].split("//")[1], "***") if "@" in cls.DATABASE_URL else cls.DATABASE_URL,
            "is_postgresql": cls.is_postgresql(),
            "is_sqlite": cls.is_sqlite(),
            "pool_size": cls.POSTGRES_POOL_SIZE if cls.is_postgresql() else None
        }

config = Config()

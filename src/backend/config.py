"""
Configuration management for the Glossary API
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/glossary.db")

    # Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "devpassword")

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
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

config = Config()

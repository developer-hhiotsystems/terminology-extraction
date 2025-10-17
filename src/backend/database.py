"""
Database session management and utilities
Provides database connection, session handling, and dependency injection for FastAPI
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os

from src.backend.config import config
from src.backend.models import Base, init_db


# Create SQLAlchemy engine
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
    echo=config.DEBUG  # Log SQL queries in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions

    Usage in FastAPI endpoints:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions

    Usage in regular Python code:
        with get_db_context() as db:
            items = db.query(Item).all()

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database():
    """
    Initialize database by creating all tables
    Should be called on application startup
    """
    # Ensure data directory exists
    db_path = config.DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    # Create all tables
    init_db(engine)
    print(f"[OK] Database initialized: {config.DATABASE_URL}")


def reset_database():
    """
    Drop and recreate all database tables
    WARNING: This will delete all data!
    Should only be used in development/testing
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[OK] Database reset complete")


def check_database_connection() -> bool:
    """
    Check if database connection is working

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with get_db_context() as db:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

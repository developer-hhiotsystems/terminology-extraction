"""
Database session management and utilities
Provides database connection, session handling, and dependency injection for FastAPI
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os
import logging

from src.backend.config import config
from src.backend.base_models import Base, init_db

logger = logging.getLogger(__name__)


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
    logger.info(f"Database initialized: {config.DATABASE_URL}")


def reset_database():
    """
    Drop and recreate all database tables
    WARNING: This will delete all data!
    Should only be used in development/testing
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database reset complete")


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
        logger.error(f"Database connection failed: {e}")
        return False


def initialize_fts5():
    """
    Initialize SQLite FTS5 full-text search index

    Creates FTS5 virtual table, triggers, and populates with existing data.
    Only works with SQLite databases (skipped for PostgreSQL).

    This should be called after initialize_database() on first setup,
    or when you want to rebuild the FTS5 index.

    Returns:
        bool: True if successful, False otherwise
    """
    # Only run for SQLite databases
    if "sqlite" not in config.DATABASE_URL.lower():
        logger.info("Skipping FTS5 initialization (not a SQLite database)")
        return False

    try:
        from sqlalchemy import text
        import os
        from pathlib import Path

        # Read the FTS5 schema SQL file
        sql_file = Path(__file__).parent.parent.parent / 'scripts' / 'create_fts5_index.sql'

        if not sql_file.exists():
            logger.error(f"FTS5 schema file not found: {sql_file}")
            return False

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Execute the schema creation
        with get_db_context() as db:
            # Split script into statements (SQLAlchemy doesn't support executescript)
            # We'll execute the key statements individually

            # 1. Drop existing table and triggers
            db.execute(text("DROP TABLE IF EXISTS glossary_fts"))
            db.execute(text("DROP TRIGGER IF EXISTS glossary_fts_insert"))
            db.execute(text("DROP TRIGGER IF EXISTS glossary_fts_update"))
            db.execute(text("DROP TRIGGER IF EXISTS glossary_fts_delete"))

            # 2. Create FTS5 virtual table
            db.execute(text("""
                CREATE VIRTUAL TABLE glossary_fts USING fts5(
                    term,
                    definition_text,
                    language UNINDEXED,
                    domain_tags UNINDEXED,
                    source UNINDEXED,
                    content='glossary_entries',
                    content_rowid='id',
                    tokenize='porter unicode61 remove_diacritics 2'
                )
            """))

            # 3. Create INSERT trigger
            db.execute(text("""
                CREATE TRIGGER glossary_fts_insert AFTER INSERT ON glossary_entries BEGIN
                    INSERT INTO glossary_fts(
                        rowid, term, definition_text, language, domain_tags, source
                    )
                    VALUES (
                        new.id,
                        new.term,
                        (
                            SELECT GROUP_CONCAT(json_extract(value, '$.text'), ' | ')
                            FROM json_each(new.definitions)
                            WHERE json_extract(value, '$.text') IS NOT NULL
                        ),
                        new.language,
                        COALESCE(
                            (
                                SELECT GROUP_CONCAT(value, ',')
                                FROM json_each(new.domain_tags)
                            ),
                            ''
                        ),
                        new.source
                    );
                END
            """))

            # 4. Create UPDATE trigger
            db.execute(text("""
                CREATE TRIGGER glossary_fts_update AFTER UPDATE ON glossary_entries BEGIN
                    DELETE FROM glossary_fts WHERE rowid = old.id;
                    INSERT INTO glossary_fts(
                        rowid, term, definition_text, language, domain_tags, source
                    )
                    VALUES (
                        new.id,
                        new.term,
                        (
                            SELECT GROUP_CONCAT(json_extract(value, '$.text'), ' | ')
                            FROM json_each(new.definitions)
                            WHERE json_extract(value, '$.text') IS NOT NULL
                        ),
                        new.language,
                        COALESCE(
                            (
                                SELECT GROUP_CONCAT(value, ',')
                                FROM json_each(new.domain_tags)
                            ),
                            ''
                        ),
                        new.source
                    );
                END
            """))

            # 5. Create DELETE trigger
            db.execute(text("""
                CREATE TRIGGER glossary_fts_delete AFTER DELETE ON glossary_entries BEGIN
                    DELETE FROM glossary_fts WHERE rowid = old.id;
                END
            """))

            # 6. Populate with existing data
            result = db.execute(text("""
                INSERT INTO glossary_fts(
                    rowid, term, definition_text, language, domain_tags, source
                )
                SELECT
                    ge.id,
                    ge.term,
                    (
                        SELECT GROUP_CONCAT(json_extract(value, '$.text'), ' | ')
                        FROM json_each(ge.definitions)
                        WHERE json_extract(value, '$.text') IS NOT NULL
                    ) AS definition_text,
                    ge.language,
                    COALESCE(
                        (
                            SELECT GROUP_CONCAT(value, ',')
                            FROM json_each(ge.domain_tags)
                        ),
                        ''
                    ) AS domain_tags,
                    ge.source
                FROM glossary_entries ge
            """))

            db.commit()

        # Verify using raw connection (FTS5 external content tables need special handling)
        import sqlite3
        db_path = config.DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verify FTS5 table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='glossary_fts'
        """)
        if not cursor.fetchone():
            logger.error("FTS5 table was not created")
            conn.close()
            return False

        # Verify search works (FTS5 external content tables can't be counted directly)
        # Test with a common word to ensure index is populated
        cursor.execute("""
            SELECT COUNT(*)
            FROM glossary_fts fts
            JOIN glossary_entries ge ON fts.rowid = ge.id
            WHERE glossary_fts MATCH 'process OR control OR system'
        """)
        search_count = cursor.fetchone()[0]

        # Get total glossary entries for comparison
        cursor.execute("SELECT COUNT(*) FROM glossary_entries")
        total_entries = cursor.fetchone()[0]

        conn.close()

        if search_count > 0:
            logger.info(f"✓ FTS5 index initialized successfully")
            logger.info(f"✓ Search verified with {search_count} results for test query")
            logger.info(f"✓ Total glossary entries: {total_entries}")
            return True
        else:
            logger.error("FTS5 index created but search returned no results")
            return False

    except Exception as e:
        logger.error(f"Failed to initialize FTS5 index: {e}", exc_info=True)
        return False


def rebuild_fts5_index():
    """
    Rebuild the FTS5 index from scratch

    Useful when:
    - FTS5 index becomes corrupted
    - You want to update tokenizer settings
    - After bulk data imports

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Rebuilding FTS5 index...")
    return initialize_fts5()

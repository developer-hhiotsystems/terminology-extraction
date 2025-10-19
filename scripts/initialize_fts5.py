#!/usr/bin/env python3
"""
SQLite FTS5 Initialization Script
==================================
Purpose: Initialize FTS5 full-text search index for glossary application

This script:
1. Creates FTS5 virtual table and triggers
2. Populates FTS5 index with existing glossary entries
3. Verifies index integrity
4. Reports statistics

Usage:
    python scripts/initialize_fts5.py

Requirements:
    - SQLite 3.9.0+ with FTS5 support
    - Existing glossary_entries table with data
"""

import sqlite3
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_path():
    """
    Get the database file path

    Returns:
        Path: Path to glossary database
    """
    # Try to get from environment variable
    db_path = os.getenv('DATABASE_URL', '').replace('sqlite:///', '')

    # Default to ./data/glossary.db if not set
    if not db_path or not db_path.endswith('.db'):
        project_root = Path(__file__).parent.parent
        db_path = project_root / 'data' / 'glossary.db'
    else:
        db_path = Path(db_path)

    return db_path


def check_sqlite_version(conn):
    """
    Check SQLite version and FTS5 support

    Args:
        conn: SQLite connection

    Returns:
        bool: True if FTS5 is supported
    """
    cursor = conn.cursor()

    # Check SQLite version
    cursor.execute("SELECT sqlite_version()")
    version = cursor.fetchone()[0]
    logger.info(f"SQLite version: {version}")

    # Check FTS5 support
    cursor.execute("PRAGMA compile_options")
    compile_options = [row[0] for row in cursor.fetchall()]

    fts5_enabled = any('FTS5' in option for option in compile_options)

    if fts5_enabled:
        logger.info("✓ FTS5 support enabled")
        return True
    else:
        logger.error("✗ FTS5 support NOT enabled in this SQLite build")
        return False


def read_sql_file(sql_file_path):
    """
    Read SQL file and split into individual statements

    Args:
        sql_file_path: Path to SQL file

    Returns:
        list: List of SQL statements
    """
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split by semicolon, but ignore comments and empty lines
    statements = []
    current_statement = []

    for line in sql_content.split('\n'):
        # Skip comment lines
        if line.strip().startswith('--') or line.strip().startswith('/*'):
            continue

        current_statement.append(line)

        # Check if line ends with semicolon
        if line.strip().endswith(';'):
            stmt = '\n'.join(current_statement).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_statement = []

    return statements


def create_fts5_schema(conn):
    """
    Create FTS5 virtual table and triggers

    Args:
        conn: SQLite connection
    """
    logger.info("Creating FTS5 schema and triggers...")

    sql_file = Path(__file__).parent / 'create_fts5_index.sql'

    if not sql_file.exists():
        logger.error(f"SQL file not found: {sql_file}")
        sys.exit(1)

    cursor = conn.cursor()

    # Read and execute SQL file
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    try:
        # Execute the entire script
        cursor.executescript(sql_script)
        conn.commit()
        logger.info("✓ FTS5 schema and triggers created successfully")
    except sqlite3.Error as e:
        logger.error(f"✗ Failed to create FTS5 schema: {e}")
        raise


def populate_fts5_index(conn):
    """
    Populate FTS5 index with existing glossary entries

    Args:
        conn: SQLite connection

    Returns:
        int: Number of entries indexed
    """
    logger.info("Populating FTS5 index with existing entries...")

    cursor = conn.cursor()

    # Count existing entries
    cursor.execute("SELECT COUNT(*) FROM glossary_entries")
    total_entries = cursor.fetchone()[0]
    logger.info(f"Found {total_entries} entries to index")

    if total_entries == 0:
        logger.warning("No entries found in glossary_entries table")
        return 0

    # Populate FTS5 index
    populate_sql = """
    INSERT INTO glossary_fts(
        rowid,
        term,
        definition_text,
        language,
        domain_tags,
        source
    )
    SELECT
        ge.id,
        ge.term,
        -- Extract all definition texts from JSON array
        (
            SELECT GROUP_CONCAT(json_extract(value, '$.text'), ' | ')
            FROM json_each(ge.definitions)
            WHERE json_extract(value, '$.text') IS NOT NULL
        ) AS definition_text,
        ge.language,
        -- Convert domain_tags to comma-separated string
        COALESCE(
            (
                SELECT GROUP_CONCAT(value, ',')
                FROM json_each(ge.domain_tags)
            ),
            ''
        ) AS domain_tags,
        ge.source
    FROM glossary_entries ge
    """

    try:
        cursor.execute(populate_sql)
        conn.commit()

        # Verify population
        cursor.execute("SELECT COUNT(*) FROM glossary_fts")
        indexed_count = cursor.fetchone()[0]

        logger.info(f"✓ Indexed {indexed_count} entries successfully")
        return indexed_count

    except sqlite3.Error as e:
        logger.error(f"✗ Failed to populate FTS5 index: {e}")
        raise


def verify_fts5_index(conn):
    """
    Verify FTS5 index integrity and run test queries

    Args:
        conn: SQLite connection
    """
    logger.info("Verifying FTS5 index...")

    cursor = conn.cursor()

    # Test 1: Check table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='glossary_fts'
    """)
    if not cursor.fetchone():
        logger.error("✗ FTS5 table not found!")
        return False

    logger.info("✓ FTS5 table exists")

    # Test 2: Check triggers exist
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='trigger' AND name LIKE 'glossary_fts_%'
    """)
    triggers = [row[0] for row in cursor.fetchall()]
    expected_triggers = ['glossary_fts_insert', 'glossary_fts_update', 'glossary_fts_delete']

    for trigger in expected_triggers:
        if trigger in triggers:
            logger.info(f"✓ Trigger exists: {trigger}")
        else:
            logger.warning(f"✗ Trigger missing: {trigger}")

    # Test 3: Run sample search query
    cursor.execute("""
        SELECT COUNT(*) FROM glossary_fts
        WHERE glossary_fts MATCH 'control OR temperature'
    """)
    search_results = cursor.fetchone()[0]
    logger.info(f"✓ Sample search found {search_results} results for 'control OR temperature'")

    # Test 4: Check BM25 ranking
    cursor.execute("""
        SELECT
            ge.term,
            bm25(glossary_fts) AS score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH 'process'
        ORDER BY score
        LIMIT 3
    """)

    top_results = cursor.fetchall()
    if top_results:
        logger.info("✓ BM25 ranking working - Top 3 results for 'process':")
        for i, (term, score) in enumerate(top_results, 1):
            logger.info(f"  {i}. {term} (score: {score:.4f})")

    return True


def print_statistics(conn):
    """
    Print FTS5 index statistics

    Args:
        conn: SQLite connection
    """
    cursor = conn.cursor()

    logger.info("\n" + "="*60)
    logger.info("FTS5 INDEX STATISTICS")
    logger.info("="*60)

    # Total entries
    cursor.execute("SELECT COUNT(*) FROM glossary_fts")
    total = cursor.fetchone()[0]
    logger.info(f"Total entries indexed: {total}")

    # Entries by language
    cursor.execute("""
        SELECT language, COUNT(*)
        FROM glossary_fts
        GROUP BY language
    """)
    logger.info("\nEntries by language:")
    for lang, count in cursor.fetchall():
        logger.info(f"  {lang}: {count}")

    # Entries by source
    cursor.execute("""
        SELECT source, COUNT(*)
        FROM glossary_fts
        GROUP BY source
        ORDER BY COUNT(*) DESC
        LIMIT 5
    """)
    logger.info("\nTop 5 sources:")
    for source, count in cursor.fetchall():
        logger.info(f"  {source}: {count}")

    # Database size
    cursor.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    db_size_mb = (page_count * page_size) / (1024 * 1024)
    logger.info(f"\nDatabase size: {db_size_mb:.2f} MB")

    logger.info("="*60 + "\n")


def main():
    """
    Main execution function
    """
    logger.info("="*60)
    logger.info("SQLite FTS5 Initialization Script")
    logger.info("="*60)

    # Get database path
    db_path = get_database_path()
    logger.info(f"Database path: {db_path}")

    # Check if database exists
    if not db_path.exists():
        logger.error(f"Database file not found: {db_path}")
        logger.error("Please run the application first to create the database")
        sys.exit(1)

    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        logger.info("✓ Connected to database")

        # Check SQLite version and FTS5 support
        if not check_sqlite_version(conn):
            logger.error("FTS5 support is required. Please upgrade SQLite.")
            sys.exit(1)

        # Create FTS5 schema and triggers
        create_fts5_schema(conn)

        # Populate FTS5 index
        indexed_count = populate_fts5_index(conn)

        # Verify index
        verify_fts5_index(conn)

        # Print statistics
        print_statistics(conn)

        # Close connection
        conn.close()

        logger.info("="*60)
        logger.info("✓ FTS5 initialization completed successfully!")
        logger.info(f"✓ {indexed_count} entries indexed and ready for search")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"✗ Initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Fix FTS table using direct SQLite3 connection
"""
import sqlite3
from pathlib import Path

# Database path
database_path = Path(__file__).parent.parent / "data" / "glossary.db"

print("Fixing FTS table with direct SQLite connection...")
print("=" * 60)

conn = sqlite3.connect(database_path)
cursor = conn.cursor()

try:
    # Drop existing triggers
    print("Dropping old triggers...")
    cursor.execute("DROP TRIGGER IF EXISTS glossary_fts_insert")
    cursor.execute("DROP TRIGGER IF EXISTS glossary_fts_update")
    cursor.execute("DROP TRIGGER IF EXISTS glossary_fts_delete")

    # Drop FTS table
    print("Dropping FTS table...")
    cursor.execute("DROP TABLE IF EXISTS glossary_fts")

    # Recreate FTS table
    print("Creating new FTS table...")
    cursor.execute("""
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
    """)

    # Recreate triggers
    print("Creating triggers...")
    cursor.execute("""
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
    """)

    cursor.execute("""
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
    """)

    cursor.execute("""
        CREATE TRIGGER glossary_fts_delete AFTER DELETE ON glossary_entries BEGIN
            DELETE FROM glossary_fts WHERE rowid = old.id;
        END
    """)

    # Repopulate FTS from existing entries
    print("Populating FTS table...")
    cursor.execute("""
        INSERT INTO glossary_fts(rowid, term, definition_text, language, domain_tags, source)
        SELECT
            id,
            term,
            (
                SELECT GROUP_CONCAT(json_extract(value, '$.text'), ' | ')
                FROM json_each(definitions)
                WHERE json_extract(value, '$.text') IS NOT NULL
            ),
            language,
            COALESCE(
                (
                    SELECT GROUP_CONCAT(value, ',')
                    FROM json_each(domain_tags)
                ),
                ''
            ),
            source
        FROM glossary_entries
    """)

    conn.commit()

    # Verify
    cursor.execute("SELECT COUNT(*) FROM glossary_fts")
    fts_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM glossary_entries")
    entries_count = cursor.fetchone()[0]

    print("=" * 60)
    print("SUCCESS! FTS table rebuilt")
    print(f"Glossary entries: {entries_count}")
    print(f"FTS entries: {fts_count}")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR: {e}")
    conn.rollback()
    raise
finally:
    conn.close()

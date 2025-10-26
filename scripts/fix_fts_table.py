"""
Fix the FTS table and triggers in the database
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Connect to database
database_path = project_root / "data" / "glossary.db"
engine = create_engine(f"sqlite:///{database_path}")
Session = sessionmaker(bind=engine)
session = Session()

print("Fixing FTS table and triggers...")
print("=" * 60)

try:
    # Drop existing triggers
    print("Dropping old triggers...")
    session.execute(text("DROP TRIGGER IF EXISTS glossary_fts_insert"))
    session.execute(text("DROP TRIGGER IF EXISTS glossary_fts_update"))
    session.execute(text("DROP TRIGGER IF EXISTS glossary_fts_delete"))

    # Drop and recreate FTS table
    print("Rebuilding FTS table...")
    session.execute(text("DROP TABLE IF EXISTS glossary_fts"))

    session.execute(text("""
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

    # Recreate triggers
    print("Creating triggers...")
    session.execute(text("""
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

    session.execute(text("""
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

    session.execute(text("""
        CREATE TRIGGER glossary_fts_delete AFTER DELETE ON glossary_entries BEGIN
            DELETE FROM glossary_fts WHERE rowid = old.id;
        END
    """))

    # Repopulate FTS from existing entries
    print("Populating FTS table from existing entries...")
    session.execute(text("""
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
    """))

    session.commit()

    # Verify
    result = session.execute(text("SELECT COUNT(*) FROM glossary_fts"))
    fts_count = result.scalar()

    print("=" * 60)
    print(f"SUCCESS! FTS table rebuilt")
    print(f"FTS entries: {fts_count}")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR: {e}")
    session.rollback()
    sys.exit(1)
finally:
    session.close()

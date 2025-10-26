"""
Test database reset functionality directly
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

print("Testing database reset...")
print("=" * 60)

try:
    # Count before
    result = session.execute(text("SELECT COUNT(*) FROM glossary_entries"))
    count_before = result.scalar()
    print(f"Entries before reset: {count_before}")

    result = session.execute(text("SELECT COUNT(*) FROM term_relationships"))
    rel_count_before = result.scalar()
    print(f"Relationships before reset: {rel_count_before}")

    # Perform reset using raw SQL (same as fixed admin.py)
    print("\nPerforming reset...")

    # Disable foreign key checks
    session.execute(text("PRAGMA foreign_keys = OFF"))

    # Drop FTS triggers to avoid conflicts
    session.execute(text("DROP TRIGGER IF EXISTS glossary_fts_insert"))
    session.execute(text("DROP TRIGGER IF EXISTS glossary_fts_update"))
    session.execute(text("DROP TRIGGER IF EXISTS glossary_fts_delete"))

    # Drop FTS table
    session.execute(text("DROP TABLE IF EXISTS glossary_fts"))

    # Delete main tables
    session.execute(text("DELETE FROM glossary_entries"))
    session.execute(text("DELETE FROM uploaded_documents"))
    session.execute(text("DELETE FROM term_relationships"))

    # Recreate FTS table
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

    # Recreate FTS triggers
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

    # Re-enable foreign key checks
    session.execute(text("PRAGMA foreign_keys = ON"))

    # Commit
    session.commit()

    # Reset auto-increment (if table exists)
    try:
        session.execute(text("DELETE FROM sqlite_sequence WHERE name='glossary_entries'"))
        session.execute(text("DELETE FROM sqlite_sequence WHERE name='uploaded_documents'"))
        session.execute(text("DELETE FROM sqlite_sequence WHERE name='term_relationships'"))
        session.commit()
    except Exception:
        # sqlite_sequence doesn't exist yet, which is fine
        pass

    # Count after
    result = session.execute(text("SELECT COUNT(*) FROM glossary_entries"))
    count_after = result.scalar()
    print(f"Entries after reset: {count_after}")

    result = session.execute(text("SELECT COUNT(*) FROM term_relationships"))
    rel_count_after = result.scalar()
    print(f"Relationships after reset: {rel_count_after}")

    print("\n" + "=" * 60)
    print("SUCCESS! Database reset completed without errors")
    print(f"Deleted {count_before} entries and {rel_count_before} relationships")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR: {e}")
    session.rollback()
    sys.exit(1)
finally:
    session.close()

"""
Database Reset Script
Drops all tables, recreates them, and seeds with default data
"""
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.backend.database import engine, SessionLocal
from src.backend.models import Base, drop_db, init_db, seed_document_types


def reset_database():
    """
    Drop all tables, recreate them, and seed with default data
    """
    print("WARNING: This will delete ALL data in the database!")
    print("=" * 60)

    try:
        # Drop all tables
        print("Dropping all tables...")
        drop_db(engine)
        print("[OK] All tables dropped")

        # Recreate all tables
        print("\nCreating all tables...")
        init_db(engine)
        print("[OK] All tables created")

        # Seed document types
        print("\nSeeding default document types...")
        session = SessionLocal()
        try:
            seed_document_types(session)
            print("[OK] Document types seeded")
        finally:
            session.close()

        print("\n" + "=" * 60)
        print("[OK] Database reset complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Error during database reset: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    reset_database()

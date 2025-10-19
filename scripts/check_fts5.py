"""Check FTS5 support and initialize index"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("FTS5 Support Check")
print("=" * 60)

# Check SQLite version
print(f"SQLite version: {sqlite3.sqlite_version}")

# Check FTS5 support
conn = sqlite3.connect('data/glossary.db')
cursor = conn.cursor()

cursor.execute('PRAGMA compile_options')
opts = [r[0] for r in cursor.fetchall()]
fts5_enabled = any('FTS5' in opt for opt in opts)

if fts5_enabled:
    print("[OK] FTS5 support: ENABLED")
else:
    print("[ERROR] FTS5 support: NOT ENABLED")
    sys.exit(1)

# Count existing glossary entries
cursor.execute("SELECT COUNT(*) FROM glossary_entries")
count = cursor.fetchone()[0]
print(f"\nExisting glossary entries: {count}")

conn.close()

# Now try to initialize FTS5
print("\n" + "=" * 60)
print("Initializing FTS5 Index")
print("=" * 60)

try:
    from src.backend.database import initialize_fts5
    result = initialize_fts5()

    if result:
        print("\n[OK] FTS5 initialization SUCCESS")

        # Verify search functionality
        conn = sqlite3.connect('data/glossary.db')
        cursor = conn.cursor()

        # Test search with JOIN (the proper way for external content FTS5)
        cursor.execute("""
            SELECT ge.term, bm25(glossary_fts) AS score
            FROM glossary_fts fts
            JOIN glossary_entries ge ON fts.rowid = ge.id
            WHERE glossary_fts MATCH 'control'
            ORDER BY score
            LIMIT 5
        """)

        results = cursor.fetchall()
        if results:
            print(f"\n[OK] Sample search results for 'control' ({len(results)} results):")
            for i, (term, score) in enumerate(results, 1):
                print(f"  {i}. {term} (score: {score:.4f})")

        # Count total searchable entries
        cursor.execute("""
            SELECT COUNT(*)
            FROM glossary_fts fts
            JOIN glossary_entries ge ON fts.rowid = ge.id
            WHERE glossary_fts MATCH 'process OR control OR temperature'
        """)
        common_terms = cursor.fetchone()[0]
        print(f"\n[OK] Found {common_terms} entries matching common technical terms")

        conn.close()
        print("\n" + "=" * 60)
        print("[SUCCESS] FTS5 is fully functional!")
        print("=" * 60)
    else:
        print("\n[ERROR] FTS5 initialization FAILED")
        sys.exit(1)

except Exception as e:
    print(f"\n✗ Error during initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

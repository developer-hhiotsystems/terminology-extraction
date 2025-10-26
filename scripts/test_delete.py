import sqlite3
import sys

try:
    conn = sqlite3.connect('data/glossary.db')
    cursor = conn.cursor()

    # Check if FTS table exists
    print("Checking if glossary_fts table exists...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='glossary_fts'")
    fts_exists = cursor.fetchone()
    print(f"FTS table exists: {bool(fts_exists)}")

    # Check triggers
    print("\nChecking triggers...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='glossary_entries'")
    triggers = cursor.fetchall()
    print(f"Found {len(triggers)} triggers:")
    for trigger in triggers:
        print(f"  - {trigger[0]}")

    # Try to delete one entry
    print("\nTrying to delete one entry...")
    cursor.execute("DELETE FROM glossary_entries WHERE id = (SELECT id FROM glossary_entries LIMIT 1)")
    conn.commit()
    print("✅ Delete successful!")

    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

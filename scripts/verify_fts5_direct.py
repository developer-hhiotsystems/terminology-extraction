"""Direct FTS5 verification using raw SQLite"""
import sqlite3

print("="*60)
print("Direct FTS5 Database Verification")
print("="*60)

conn = sqlite3.connect('data/glossary.db')
cursor = conn.cursor()

# Check if FTS5 table exists
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND name='glossary_fts'
""")
result = cursor.fetchone()
if result:
    print(f"[OK] glossary_fts table exists: {result[0]}")
else:
    print("[ERROR] glossary_fts table does NOT exist")
    exit(1)

# Check if triggers exist
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='trigger' AND name LIKE 'glossary_fts_%'
""")
triggers = cursor.fetchall()
print(f"\n[OK] Found {len(triggers)} triggers:")
for trigger in triggers:
    print(f"  - {trigger[0]}")

# Try different count approaches
print("\nTrying different count methods:")

# Method 1: Simple SELECT
try:
    cursor.execute("SELECT * FROM glossary_fts LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"[OK] Method 1: Can SELECT from glossary_fts")
        print(f"    Sample row: {row[:3] if len(row) > 3 else row}")
except Exception as e:
    print(f"[ERROR] Method 1 failed: {e}")

# Method 2: Count with WHERE clause
try:
    cursor.execute("SELECT COUNT(*) FROM glossary_fts WHERE rowid > 0")
    count = cursor.fetchone()[0]
    print(f"[OK] Method 2: COUNT with WHERE = {count}")
except Exception as e:
    print(f"[ERROR] Method 2 failed: {e}")

# Method 3: Join with main table
try:
    cursor.execute("""
        SELECT COUNT(*)
        FROM glossary_entries ge
        WHERE EXISTS (SELECT 1 FROM glossary_fts WHERE rowid = ge.id)
    """)
    count = cursor.fetchone()[0]
    print(f"[OK] Method 3: COUNT via JOIN = {count}")
except Exception as e:
    print(f"[ERROR] Method 3 failed: {e}")

# Method 4: MATCH query
try:
    cursor.execute("""
        SELECT COUNT(*) FROM glossary_fts WHERE glossary_fts MATCH '*'
    """)
    count = cursor.fetchone()[0]
    print(f"[OK] Method 4: COUNT with MATCH = {count}")
except Exception as e:
    print(f"[ERROR] Method 4 failed: {e}")

# Test actual search
try:
    cursor.execute("""
        SELECT ge.term, bm25(glossary_fts) as score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH 'control'
        ORDER BY score
        LIMIT 3
    """)
    results = cursor.fetchall()
    print(f"\n[OK] Sample search for 'control' ({len(results)} results):")
    for i, (term, score) in enumerate(results, 1):
        print(f"  {i}. {term} (score: {score:.4f})")
except Exception as e:
    print(f"[ERROR] Search failed: {e}")

conn.close()
print("\n" + "="*60)
print("[SUCCESS] FTS5 verification complete")
print("="*60)

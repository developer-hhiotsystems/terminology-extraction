"""Debug search API errors"""
import sqlite3
from pathlib import Path

# Direct SQLite test
conn = sqlite3.connect('data/glossary.db')
cursor = conn.cursor()

print("Testing FTS5 queries directly...")
print("="*60)

# Test 1: Simple search (failing in API)
print("\n[Test 1] Simple search: control")
try:
    sql = """
        SELECT
            ge.id,
            ge.term,
            ge.definitions,
            ge.language,
            ge.source,
            ge.domain_tags,
            bm25(glossary_fts) AS relevance_score,
            snippet(glossary_fts, 1, '<mark>', '</mark>', '...', 32) AS snippet
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH 'control'
        ORDER BY relevance_score
        LIMIT 3
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"[OK] Found {len(rows)} results")
    for row in rows[:3]:
        print(f"  - {row[1]} (score: {row[6]:.4f})")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 2: Count query (might be failing)
print("\n[Test 2] Count query with subselect")
try:
    sql = """
        SELECT COUNT(*)
        FROM (
            SELECT ge.id
            FROM glossary_fts fts
            JOIN glossary_entries ge ON fts.rowid = ge.id
            WHERE glossary_fts MATCH 'control'
        ) AS search_results
    """
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    print(f"[OK] Count: {count}")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 3: Boolean search
print("\n[Test 3] Boolean AND search")
try:
    sql = """
        SELECT ge.term, bm25(glossary_fts) AS score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH 'temperature AND control'
        ORDER BY score
        LIMIT 3
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"[OK] Found {len(rows)} results")
    for term, score in rows:
        print(f"  - {term} (score: {score:.4f})")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 4: Wildcard search
print("\n[Test 4] Wildcard search: temp*")
try:
    sql = """
        SELECT ge.term, bm25(glossary_fts) AS score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH 'temp*'
        ORDER BY score
        LIMIT 3
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"[OK] Found {len(rows)} results")
    for term, score in rows:
        print(f"  - {term} (score: {score:.4f})")
except Exception as e:
    print(f"[ERROR] {e}")

conn.close()
print("\n" + "="*60)
print("Direct SQLite tests complete!")

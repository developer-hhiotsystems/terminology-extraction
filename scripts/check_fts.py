import sqlite3

conn = sqlite3.connect('data/glossary.db')
cursor = conn.cursor()

print("=== FTS Table Structure ===\n")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='glossary_fts'")
result = cursor.fetchone()
if result:
    print(result[0])
    print("\n")

print("=== FTS Table Info ===\n")
cursor.execute("PRAGMA table_info(glossary_fts)")
for row in cursor.fetchall():
    print(f"{row[1]}: {row[2]}")

print("\n=== All Triggers ===\n")
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='glossary_entries'")
for name, sql in cursor.fetchall():
    print(f"\n{name}:")
    print(sql)
    print("-" * 60)

conn.close()

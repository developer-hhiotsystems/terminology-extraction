import sqlite3

conn = sqlite3.connect('data/glossary.db')
cursor = conn.cursor()

print("=== Checking DELETE trigger definition ===\n")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name='glossary_fts_delete'")
result = cursor.fetchone()

if result:
    print(result[0])
else:
    print("Trigger not found!")

conn.close()

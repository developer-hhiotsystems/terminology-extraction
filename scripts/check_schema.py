import sqlite3

conn = sqlite3.connect('data/glossary.db')
cursor = conn.cursor()

print("=== glossary_entries table schema ===")
cursor.execute("PRAGMA table_info(glossary_entries)")
for row in cursor.fetchall():
    print(f"{row[1]}: {row[2]}")

conn.close()

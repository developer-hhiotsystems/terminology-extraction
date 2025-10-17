# Data Directory

This folder contains runtime data files for the Glossary Extraction application.

## 📂 Directory Structure

```
data/
├── glossary.db          # SQLite database (auto-created, NOT in Git)
├── uploads/             # Uploaded PDF documents
└── iate/                # IATE terminology dataset (optional)
```

## 🗄️ Database File

**File:** `glossary.db`
**Type:** SQLite database
**Size:** ~100 KB (empty), grows with usage
**Status:** ✅ Auto-created on first run

The database contains 4 tables:
- `glossary_entries` - Terminology with definitions
- `terminology_cache` - Cached API responses
- `sync_logs` - Neo4j sync tracking
- `uploaded_documents` - File metadata

## 🔍 Viewing the Database

**Option 1: VS Code Extension**
Install: SQLite Viewer (by alexcvzz)
Then right-click `glossary.db` → Open Database

**Option 2: Command Line**
```bash
sqlite3 data/glossary.db
.tables              # Show all tables
.schema glossary_entries   # Show table structure
SELECT * FROM glossary_entries;  # Query data
.quit
```

**Option 3: DB Browser for SQLite**
Free GUI tool: https://sqlitebrowser.org/

## ⚠️ Important Notes

- **Database is NOT in Git** (excluded by `.gitignore`)
- **Created automatically** when you run the backend
- **Location configured in** `.env` file: `DATABASE_URL=sqlite:///./data/glossary.db`
- **Backup regularly** (backups go to `backups/sqlite/`)

## 🚀 First Time Setup

The database is created automatically when you start the backend:

```bash
python src/backend/app.py
```

You'll see:
```
Starting Glossary Extraction API...
[OK] Database initialized: sqlite:///./data/glossary.db
```

Check it exists:
```bash
ls -lh data/glossary.db
```

## 📊 Current Schema

**Last Updated:** 2025-10-17

Tables created with:
- Primary keys and indexes
- Foreign key constraints
- CHECK constraints for enums
- Automatic timestamps
- JSON field support

See `src/backend/models.py` for full schema definition.

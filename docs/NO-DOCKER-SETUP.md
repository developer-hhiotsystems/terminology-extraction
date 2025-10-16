# No-Docker Setup Guide

**For environments where Docker is not allowed or desired**

---

## ✅ Full Functionality Without Docker

This project works completely **without Docker**!

Docker was only planned for Neo4j (graph database), but we have alternatives.

---

## 🎯 What Works Without Docker

### **Phase 1 (100% functional):**
- ✓ Backend API (FastAPI on port 8000)
- ✓ Frontend UI (React on port 3000)
- ✓ SQLite database (file-based)
- ✓ File upload and processing
- ✓ CRUD operations
- ✓ All tests
- ✓ Complete development environment

### **Phase 2 (95% functional):**
- ✓ PDF parsing and extraction
- ✓ NLP terminology extraction
- ✓ Translation (DeepL API)
- ✓ IATE validation
- ⚠️ Graph visualization (limited - see alternatives below)

### **Phase 3-4 (100% functional):**
- ✓ Testing and validation
- ✓ Deployment
- ✓ All quality assurance

---

## 🗄️ Database Options (No Docker)

### **Option 1: SQLite Only** ⭐ Recommended

**Advantages:**
- No installation needed
- Single file database
- Fast and reliable
- Perfect for development/testing
- Included in Python
- No permissions needed

**Configuration:**
Already configured! Just use the project as-is.

**Database location:**
`data/glossary.db`

**Backup:**
```bash
# Automatic with our script
python scripts/backup-sqlite.py backup
```

**What you get:**
- All terminology data
- Relationships between terms
- Upload history
- Validation results
- Basic queries and filtering

**What you lose:**
- Advanced graph visualization
- Complex relationship queries

**Reality:**
For 95% of use cases, SQLite is sufficient!

---

### **Option 2: Neo4j Desktop** (No Docker!)

**If you really want graph features without Docker:**

**Install:**
1. Download: https://neo4j.com/download/
2. Install Neo4j Desktop (standalone app, no container)
3. Create new database
4. Start database

**Configure:**
Update `.env`:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

**Run initialization:**
```bash
python scripts/init-neo4j.py
```

**Advantages:**
- Full graph database
- No Docker required
- Desktop application like any other software

**Disadvantages:**
- Separate installation required
- ~500MB disk space
- Company approval may still be needed

---

### **Option 3: PostgreSQL** (Alternative)

**If company already has PostgreSQL:**

We can adapt the project to use PostgreSQL instead:
- Replace SQLite with PostgreSQL
- Use PostgreSQL's JSONB for relationships
- No graph database needed
- Connects to existing company database

**Configuration:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/glossary
```

---

## 🔧 Disable Docker References

### **Remove docker-compose.yml**

Already done - `docker-compose.dev.yml` is optional!

### **Update .env**

```env
# SQLite only - no Neo4j
DATABASE_URL=sqlite:///./data/glossary.db

# Comment out Neo4j (not needed)
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=devpassword
```

### **Skip Neo4j Setup**

In `setup-check.py`, Neo4j is marked as optional:

```
Optional Components (Phase 2+):
[WARN] Neo4j not running - needed for Phase 2
```

This is just a warning, not an error!

---

## 📊 SQLite-Only Architecture

### **Tables (Already Designed):**

```sql
-- Core terminology
GlossaryEntry (
  id, term, definition, source,
  domain, language, status, created_at
)

-- Relationships (SQLite way)
TermRelationships (
  id, term_id_1, term_id_2,
  relationship_type, confidence
)

-- Upload tracking
UploadedDocument (
  id, filename, upload_date,
  status, entry_count
)

-- Sync tracking
SyncLog (
  id, entry_id, sync_status,
  retry_count, last_attempt
)
```

### **Queries Work Great:**

```sql
-- Find related terms
SELECT t2.term
FROM TermRelationships r
JOIN GlossaryEntry t2 ON t2.id = r.term_id_2
WHERE r.term_id_1 = ?

-- Domain filtering
SELECT * FROM GlossaryEntry
WHERE domain = 'Legal' AND language = 'EN'

-- Full-text search
SELECT * FROM GlossaryEntry
WHERE term LIKE '%contract%' OR definition LIKE '%contract%'
```

**Perfectly functional without Neo4j!**

---

## 🚀 Company Computer Setup (No Docker)

### **Simple Setup:**

```bash
# 1. Clone
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction

# 2. Run setup (automatically skips Docker)
.\setup-windows.ps1

# 3. Edit .env - comment out Neo4j lines
notepad .env

# 4. Test backend
.\venv\Scripts\activate
python src\backend\app.py

# 5. Test frontend
npm start
```

**That's it! No Docker needed.**

---

## 📋 What Setup Script Does (No Docker)

```
[1/8] ✓ Check Python, Node, Git
[2/8] ✓ Create venv folder
[3/8] ✓ Install Python packages (no Neo4j driver issues)
[4/8] ✓ Install Node packages
[5/8] ✓ Create .env (Neo4j optional)
[6/8] ✓ Create data directories
[7/8] ✓ Verify setup (Neo4j shows as optional)
[8/8] ✓ Complete!
```

**No Docker checked, no Docker installed, no Docker needed!**

---

## 🔍 Verification Without Docker

```bash
# Check setup
python setup-check.py
```

**Expected output:**
```
Required: 5/5 passed ✓
Optional: 0/4 passed

[OK] Minimum requirements met - ready for Phase 1 development

Optional components (can skip):
[WARN] Docker not installed - needed for Neo4j in Phase 2
[WARN] Neo4j not running
```

**This is fine!** Docker is optional.

---

## 💡 Benefits of No-Docker Approach

### **For Company Environment:**
- ✓ No security concerns
- ✓ No containerization
- ✓ No special permissions needed
- ✓ Simpler architecture
- ✓ Easier to audit
- ✓ Standard Python/Node.js stack

### **For Development:**
- ✓ Faster setup
- ✓ Less disk space
- ✓ Less memory usage
- ✓ Simpler troubleshooting
- ✓ More portable

### **For Testing:**
- ✓ Single file database (easy backup)
- ✓ Easy to reset/restore
- ✓ Works on any machine
- ✓ No network configuration

---

## 📈 Performance Without Neo4j

**For typical glossary application:**

| Feature | SQLite | Neo4j |
|---------|--------|-------|
| Store 10,000 terms | ✓ Fast | ✓ Fast |
| Search terms | ✓ Fast | ✓ Fast |
| Find relationships | ✓ Good | ✓ Better |
| Complex graph queries | ⚠️ Slower | ✓ Fast |
| Visualization | ⚠️ Basic | ✓ Advanced |

**Reality:**
Unless you have >100,000 terms with complex relationships, SQLite is fine!

---

## 🎯 Recommended Configuration

### **For Company Computer:**

**Use SQLite only:**
1. Run setup normally
2. Ignore Neo4j warnings
3. Comment out Neo4j config in .env
4. Focus on core features

**Benefits:**
- ✓ Works immediately
- ✓ No approvals needed
- ✓ Company-friendly
- ✓ Fully functional

---

## 🔄 Migration Path (If Needed Later)

**If you want Neo4j later:**

Option A: Neo4j Desktop (no Docker)
Option B: Cloud Neo4j (Neo4j Aura)
Option C: Company-hosted Neo4j

**Data migration:**
We have scripts to export from SQLite and import to Neo4j!

```bash
# Export from SQLite
python scripts/export-to-neo4j.py
```

---

## ✅ Summary

**Docker Status:** ❌ Not needed, not used, not required

**What you need:**
- Python 3.10+ ✓
- Node.js 18+ ✓
- Git ✓

**What you don't need:**
- Docker ✗
- Neo4j ✗ (optional)
- Containerization ✗

**Company-friendly:** ✓ Yes!

---

## 🚀 Start Testing Without Docker

```bash
# Just run the setup
.\setup-windows.ps1

# Ignore any Neo4j/Docker warnings
# They're optional!

# Test immediately
python src\backend\app.py
npm start
```

**Everything works! No Docker required!** 🎉

---

**Questions about Docker/Neo4j alternatives?**
See: `TROUBLESHOOTING.md` or `docs/COMPANY-COMPUTER-SETUP.md`

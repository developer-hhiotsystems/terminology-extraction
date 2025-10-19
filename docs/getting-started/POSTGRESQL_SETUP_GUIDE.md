# PostgreSQL Setup Guide
## Quick Start for Glossary Application Migration

**Last Updated:** 2025-10-19
**Target:** Month 2 - PostgreSQL Migration

---

## 📋 Prerequisites

- Python 3.9+
- pip package manager
- PostgreSQL 16+ (or Docker)

---

## 🚀 Quick Start (Docker - Recommended)

### Option A: Docker Compose (Easiest)

**1. Start PostgreSQL with Docker Compose:**
```bash
# Start PostgreSQL and pgAdmin
docker-compose -f docker-compose.postgresql.yml up -d

# Verify it's running
docker-compose -f docker-compose.postgresql.yml ps

# View logs
docker-compose -f docker-compose.postgresql.yml logs -f postgres
```

**2. Access PostgreSQL:**
- **PostgreSQL:** `localhost:5432`
- **pgAdmin:** http://localhost:5050
  - Email: `admin@glossary.local`
  - Password: `admin`

**3. Configure Application:**
```bash
# Copy environment template
cp .env.postgresql.example .env

# Edit .env and verify settings
# DATABASE_TYPE=postgresql should be set
```

**4. Install Python Dependencies:**
```bash
pip install -r requirements-postgresql.txt
```

**5. Done!** Your application will now use PostgreSQL.

---

### Option B: Manual Docker Run

```bash
# Run PostgreSQL container
docker run -d \
  --name glossary-postgres \
  -e POSTGRES_DB=glossary \
  -e POSTGRES_USER=glossary_user \
  -e POSTGRES_PASSWORD=glossary_password \
  -p 5432:5432 \
  -v glossary_postgres_data:/var/lib/postgresql/data \
  postgres:16-alpine

# Verify it's running
docker ps | grep glossary-postgres

# Test connection
docker exec -it glossary-postgres psql -U glossary_user -d glossary -c "SELECT version();"
```

---

## 🔧 Manual Installation (Without Docker)

### Windows

**1. Download PostgreSQL:**
- Visit: https://www.postgresql.org/download/windows/
- Download PostgreSQL 16.x installer
- Run installer and follow wizard

**2. During Installation:**
- Set password for postgres user
- Port: 5432 (default)
- Locale: English, United States
- Components: PostgreSQL Server, pgAdmin 4, Command Line Tools

**3. Create Database and User:**
```sql
-- Open pgAdmin or psql
-- Connect as postgres user

-- Create database
CREATE DATABASE glossary;

-- Create user
CREATE USER glossary_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE glossary TO glossary_user;

-- Connect to glossary database
\c glossary

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO glossary_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO glossary_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO glossary_user;
```

**4. Update Environment:**
```bash
# Edit .env file
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=glossary
POSTGRES_USER=glossary_user
POSTGRES_PASSWORD=your_secure_password
```

---

### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE glossary;
CREATE USER glossary_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE glossary TO glossary_user;
\c glossary
GRANT ALL ON SCHEMA public TO glossary_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO glossary_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO glossary_user;
EOF
```

---

### macOS

```bash
# Using Homebrew
brew install postgresql@16
brew services start postgresql@16

# Create database and user
psql postgres <<EOF
CREATE DATABASE glossary;
CREATE USER glossary_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE glossary TO glossary_user;
EOF
```

---

## 🔄 Migration from SQLite

### Step 1: Backup Current SQLite Database

```bash
# Create backup directory
mkdir -p backups/sqlite

# Copy current database
cp data/glossary.db backups/sqlite/glossary_$(date +%Y%m%d_%H%M%S).db
```

### Step 2: Install PostgreSQL Dependencies

```bash
pip install -r requirements-postgresql.txt
```

### Step 3: Configure for PostgreSQL

```bash
# Update .env
DATABASE_TYPE=postgresql

# Or set environment variable
export DATABASE_TYPE=postgresql
```

### Step 4: Run Migration Script (Coming Soon)

```bash
# This will be created in Phase 3 of migration
python scripts/migrate_sqlite_to_postgresql.py
```

---

## ✅ Verify Installation

### Test PostgreSQL Connection

```bash
# Using psql
psql -h localhost -U glossary_user -d glossary -c "SELECT version();"

# Using Python
python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://glossary_user:glossary_password@localhost:5432/glossary')
with engine.connect() as conn:
    result = conn.execute('SELECT version();')
    print(result.fetchone())
"
```

### Test Application Connection

```bash
# Start the backend
cd src/backend
python app.py

# Check health endpoint
curl http://localhost:9123/health

# Check database info endpoint (if available)
curl http://localhost:9123/api/admin/database-info
```

---

## 🎯 Next Steps

Once PostgreSQL is set up:

1. ✅ PostgreSQL installed and running
2. ✅ Database and user created
3. ✅ Python dependencies installed
4. ✅ Environment configured

**Ready for:**
- Schema creation
- Data migration from SQLite
- Full-text search implementation
- Performance testing

---

## 🔍 Troubleshooting

### Connection Refused

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
```bash
# Check if PostgreSQL is running
# Docker:
docker ps | grep postgres

# Linux:
sudo systemctl status postgresql

# macOS:
brew services list | grep postgresql

# Windows:
# Check Services app for PostgreSQL service
```

### Authentication Failed

**Error:** `FATAL: password authentication failed`

**Solutions:**
1. Verify password in .env matches database user password
2. Check pg_hba.conf for authentication method
3. Reset password:
   ```sql
   ALTER USER glossary_user WITH PASSWORD 'new_password';
   ```

### Port Already in Use

**Error:** `port 5432 is already in use`

**Solutions:**
```bash
# Find what's using port 5432
# Windows:
netstat -ano | findstr :5432

# Linux/macOS:
lsof -i :5432

# Stop conflicting service or use different port
docker run -p 5433:5432 ...  # Use different host port
```

### Permission Denied

**Error:** `permission denied for schema public`

**Solutions:**
```sql
-- Run as postgres superuser
GRANT ALL ON SCHEMA public TO glossary_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO glossary_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO glossary_user;
```

---

## 📚 Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/16/
- SQLAlchemy PostgreSQL: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
- psycopg2 Documentation: https://www.psycopg.org/docs/
- Alembic Migrations: https://alembic.sqlalchemy.org/

---

## 🔐 Security Best Practices

1. **Never use default passwords in production**
2. **Use environment variables for credentials**
3. **Enable SSL for remote connections**
4. **Restrict network access** (firewall rules)
5. **Regular backups** with pg_dump
6. **Monitor connection pools** for leaks
7. **Keep PostgreSQL updated** for security patches

---

## 🎉 You're Ready!

PostgreSQL is now set up and ready for the Glossary Application migration.

**Next:** Proceed with schema creation and data migration in Month 2, Week 5.

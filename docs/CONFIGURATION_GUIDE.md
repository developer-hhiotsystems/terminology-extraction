# Configuration Management Guide

## Overview

The Glossary App uses environment-based configuration management with Pydantic for validation and type safety. Configuration can be customized per environment (development, staging, production) using environment variables or `.env` files.

---

## Quick Start

### 1. Create Configuration File

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env  # or your editor
```

### 2. Set Environment

```bash
# Development (default)
ENVIRONMENT=development

# Staging
ENVIRONMENT=staging

# Production
ENVIRONMENT=production
```

### 3. Generate Secret Key (Production)

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
SECRET_KEY=your-generated-key-here
```

---

## Configuration Files

### .env.example
Template with all available options and documentation.
Copy this to create your `.env` file.

### .env
Your actual configuration (gitignored, never commit!)
Values here override defaults.

### config/environments/
Pre-configured environment templates:
- `development.env` - Local development
- `staging.env` - Staging/testing environment
- `production.env` - Production deployment

---

## Configuration Structure

### Application Settings
```env
APP_NAME=Glossary App
APP_VERSION=1.0.0
ENVIRONMENT=development  # development, staging, production
DEBUG=true
```

### Server Configuration
```env
API_HOST=0.0.0.0
API_PORT=9123
API_WORKERS=4  # Number of Uvicorn workers
RELOAD=false   # Auto-reload on code changes (dev only!)
```

### Database
```env
DATABASE_URL=sqlite:///data/glossary.db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### Logging
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR=logs
LOG_FORMAT=json  # json or text
LOG_MAX_BYTES=10485760  # 10 MB per file
LOG_BACKUP_COUNT=10
```

### Security
```env
# REQUIRED in production!
SECRET_KEY=your-secret-key-here

# CORS
ALLOWED_ORIGINS=https://yourglossary.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,PATCH
ALLOWED_HEADERS=*

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100  # requests
RATE_LIMIT_WINDOW=60     # seconds
```

### Backup
```env
BACKUP_ENABLED=true
BACKUP_DIR=backups
BACKUP_RETENTION_DAYS=30
BACKUP_COMPRESS=true
BACKUP_VERIFY=true
BACKUP_SCHEDULE=0 2 * * *  # Cron format
```

### Health Monitoring
```env
HEALTH_CHECK_ENABLED=true
DISK_WARNING_THRESHOLD_GB=5.0
DISK_CRITICAL_THRESHOLD_GB=1.0
MEMORY_WARNING_THRESHOLD_PERCENT=85.0
MEMORY_CRITICAL_THRESHOLD_PERCENT=95.0
```

### Error Tracking (Sentry)
```env
SENTRY_ENABLED=true
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_ENVIRONMENT=production
```

---

## Usage in Code

### Get Settings
```python
from config.settings import get_settings

settings = get_settings()

# Access configuration
print(settings.DATABASE_URL)
print(settings.LOG_LEVEL)
print(settings.is_production)
```

### Use in Dependencies
```python
from fastapi import Depends
from config.settings import get_settings, Settings

@app.get("/config")
def get_config(settings: Settings = Depends(get_settings)):
    return {
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }
```

### Validate Production Config
```python
from config.settings import get_settings, validate_production_config

settings = get_settings()

# Validate before starting
if settings.is_production:
    validate_production_config(settings)
```

### Print Current Config
```python
from config.settings import get_settings

settings = get_settings()
settings.print_config()  # Prints all settings (secrets redacted)
```

---

## Environment-Specific Configuration

### Development
```bash
# Use development template
cp config/environments/development.env .env

# Or set specific vars
echo "ENVIRONMENT=development" > .env
echo "DEBUG=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
```

**Characteristics:**
- ✅ Debug mode enabled
- ✅ Auto-reload on code changes
- ✅ Detailed error messages
- ✅ API docs enabled (/docs)
- ✅ Less strict validation
- ❌ No rate limiting
- ❌ Backups disabled
- ❌ Sentry disabled

### Staging
```bash
# Use staging template
cp config/environments/staging.env .env

# Set required secrets
nano .env  # Add SECRET_KEY and SENTRY_DSN
```

**Characteristics:**
- ✅ Production-like setup
- ✅ Error tracking enabled
- ✅ API docs enabled (for testing)
- ✅ Backups enabled (shorter retention)
- ❌ Debug disabled
- ❌ Auto-reload disabled

### Production
```bash
# Use production template
cp config/environments/production.env .env

# REQUIRED: Set all secrets
nano .env  # Add SECRET_KEY, SENTRY_DSN, SMTP credentials
```

**Characteristics:**
- ✅ Optimized for performance
- ✅ All security features enabled
- ✅ Backups with long retention
- ✅ Error tracking mandatory
- ✅ Email notifications
- ✅ Metrics and monitoring
- ❌ Debug completely disabled
- ❌ API docs disabled
- ❌ No error details exposed

---

## Production Validation

The system automatically validates production configuration:

```python
# In app.py startup
from config.settings import get_settings, validate_production_config

@app.on_event("startup")
async def startup_event():
    settings = get_settings()

    if settings.is_production:
        validate_production_config(settings)
```

**Validation Checks:**
- ✅ SECRET_KEY changed from default
- ✅ DEBUG is False
- ✅ RELOAD is False
- ✅ API docs disabled
- ✅ Backups enabled
- ✅ Health checks enabled
- ✅ No wildcard CORS
- ⚠️  Sentry enabled (warning if not)

---

## Security Best Practices

### 1. Never Commit Secrets
```bash
# .gitignore already includes:
.env
.env.local
.env.production
*.env
```

### 2. Generate Strong SECRET_KEY
```bash
# Generate 32-byte URL-safe key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Result (example):
# dGhpc19pc19hX3NlY3JldF9rZXlfZXhhbXBsZQ
```

### 3. Use Different Keys Per Environment
```bash
# Development
SECRET_KEY=dev-key-12345

# Staging
SECRET_KEY=staging-key-67890

# Production
SECRET_KEY=prod-key-abcdef  # Different from others!
```

### 4. Restrict CORS in Production
```bash
# Development (allow all local)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Production (specific domain only)
ALLOWED_ORIGINS=https://yourglossary.com,https://www.yourglossary.com
```

### 5. Use Environment Variables on Server
```bash
# Instead of .env file, use system environment
export SECRET_KEY=prod-key-abcdef
export SENTRY_DSN=https://...
export DATABASE_URL=sqlite:///var/lib/glossary/data.db
```

---

## Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment defaults (override with -e or docker-compose)
ENV ENVIRONMENT=production
ENV API_HOST=0.0.0.0
ENV API_PORT=9123

# Run application
CMD ["uvicorn", "src.backend.app:app", "--host", "0.0.0.0", "--port", "9123"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  glossary-api:
    build: .
    ports:
      - "9123:9123"
    environment:
      ENVIRONMENT: production
      SECRET_KEY: ${SECRET_KEY}
      SENTRY_DSN: ${SENTRY_DSN}
      DATABASE_URL: sqlite:///data/glossary.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backups:/app/backups
    restart: unless-stopped
```

### .env for Docker Compose
```env
SECRET_KEY=your-production-key
SENTRY_DSN=https://your-dsn@sentry.io/project
```

### Run with Docker Compose
```bash
# Start with environment variables
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Kubernetes Configuration

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: glossary-config
data:
  ENVIRONMENT: production
  API_HOST: "0.0.0.0"
  API_PORT: "9123"
  LOG_LEVEL: INFO
  BACKUP_ENABLED: "true"
  HEALTH_CHECK_ENABLED: "true"
```

### Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: glossary-secrets
type: Opaque
stringData:
  SECRET_KEY: your-production-key
  SENTRY_DSN: https://your-dsn@sentry.io/project
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: glossary-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: glossary-api
        image: glossary-app:1.0.0
        ports:
        - containerPort: 9123
        envFrom:
        - configMapRef:
            name: glossary-config
        - secretRef:
            name: glossary-secrets
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: glossary-data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: glossary-logs-pvc
```

---

## Troubleshooting

### Issue: Configuration Not Loading

**Symptom:** Settings not being applied

**Check:**
```bash
# 1. Verify .env file exists
ls -la .env

# 2. Check file permissions
chmod 644 .env

# 3. Verify format (no spaces around =)
cat .env
# Correct:   KEY=value
# Incorrect: KEY = value

# 4. Print loaded config
python -c "from config.settings import get_settings; get_settings().print_config()"
```

---

### Issue: Production Validation Failing

**Symptom:** ValueError on startup in production

**Solutions:**
```bash
# 1. Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Add to .env: SECRET_KEY=...

# 2. Disable DEBUG
echo "DEBUG=false" >> .env

# 3. Disable RELOAD
echo "RELOAD=false" >> .env

# 4. Disable docs
echo "DOCS_ENABLED=false" >> .env

# 5. Validate
python -c "
from config.settings import get_settings, validate_production_config
settings = get_settings()
validate_production_config(settings)
print('✓ Production config valid!')
"
```

---

### Issue: CORS Errors

**Symptom:** Frontend can't access API

**Solution:**
```bash
# Add frontend URL to ALLOWED_ORIGINS
echo "ALLOWED_ORIGINS=https://yourglossary.com,https://www.yourglossary.com" >> .env

# Multiple origins (comma-separated, no spaces)
ALLOWED_ORIGINS=https://app1.com,https://app2.com,https://app3.com
```

---

### Issue: Database Connection Errors

**Symptom:** Can't connect to database

**Check:**
```bash
# 1. Verify database path in config
cat .env | grep DATABASE_URL

# 2. Check file exists
ls -la data/glossary.db

# 3. Check permissions
chmod 644 data/glossary.db
chmod 755 data

# 4. Test connection
sqlite3 data/glossary.db "SELECT COUNT(*) FROM glossary_entries;"
```

---

## Summary

The configuration system provides:

✅ **Type-Safe Configuration** - Pydantic validation
✅ **Environment-Specific** - Development, staging, production configs
✅ **Secret Management** - Gitignored .env files, environment variables
✅ **Production Validation** - Automatic checks for production deployment
✅ **Docker & Kubernetes Ready** - Easy integration with containers
✅ **Flexible** - Override any setting with environment variables
✅ **Documented** - Comprehensive .env.example template

**Next Steps:**
1. Copy `.env.example` to `.env`
2. Generate SECRET_KEY for production
3. Configure environment-specific settings
4. Validate production config before deployment
5. Use environment variables on production server

---

**Last Updated:** 2025-10-19
**Version:** 1.0.0
**Status:** Production Ready ✅

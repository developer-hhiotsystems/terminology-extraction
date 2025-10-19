# Deployment Strategy - Glossary Application

**Version:** 1.0
**Last Updated:** 2025-10-19
**Status:** Production Readiness Roadmap

---

## Table of Contents

1. [Production Readiness Assessment](#1-production-readiness-assessment)
2. [Containerization Strategy](#2-containerization-strategy)
3. [CI/CD Pipeline](#3-cicd-pipeline)
4. [Infrastructure & Hosting](#4-infrastructure--hosting)
5. [Monitoring & Observability](#5-monitoring--observability)
6. [Implementation Timeline](#6-implementation-timeline)
7. [Security Checklist](#7-security-checklist)
8. [Cost Estimates](#8-cost-estimates)

---

## 1. Production Readiness Assessment

### 1.1 What's Ready ✅

**Security:**
- ✅ Environment variables properly managed (.env file, not committed)
- ✅ No hardcoded passwords in codebase
- ✅ CORS configured (needs production URL update)
- ✅ SQLite with proper file permissions
- ✅ Input validation via Pydantic schemas

**Code Quality:**
- ✅ Structured modular architecture (backend/frontend separation)
- ✅ Error handling implemented
- ✅ Logging configured (basic level)
- ✅ Health check endpoint (`/health`)
- ✅ API documentation (FastAPI Swagger)

**Testing:**
- ✅ Test framework set up (pytest, Cypress)
- ✅ Unit tests for database models (13 passing)
- ✅ Test coverage tracking configured

**Development Tools:**
- ✅ Local development environment working
- ✅ Scripts for startup (start.sh, start.bat, start.ps1)
- ✅ Documentation for setup

### 1.2 What's Missing ❌

**Critical Blockers:**
- ❌ No Dockerfiles for containerization
- ❌ No CI/CD pipeline (no GitHub Actions workflows)
- ❌ No production-ready database (SQLite not suitable for production scale)
- ❌ No automated database migrations (Alembic present but not configured)
- ❌ No SSL/HTTPS configuration
- ❌ No production logging strategy (file rotation, centralized logs)
- ❌ No backup automation
- ❌ No monitoring/alerting system
- ❌ No load balancing or scaling strategy

**Infrastructure Gaps:**
- ❌ No hosting environment configured
- ❌ No CDN for static assets
- ❌ No file storage solution for PDFs (currently local filesystem)
- ❌ No database connection pooling for production
- ❌ No rate limiting on API endpoints
- ❌ No API key management for external services (DeepL, IATE)

**DevOps Gaps:**
- ❌ No staging environment
- ❌ No deployment rollback strategy
- ❌ No health check monitoring
- ❌ No performance benchmarks
- ❌ No disaster recovery plan

### 1.3 Risk Assessment

**High Risk:**
1. **SQLite in Production** - Not designed for concurrent writes, no clustering
2. **No Backup Strategy** - Data loss risk
3. **No Monitoring** - Cannot detect outages or performance issues
4. **Manual Deployment** - Error-prone, slow, no rollback

**Medium Risk:**
1. **File Storage** - Local filesystem not scalable
2. **No Rate Limiting** - Vulnerable to abuse
3. **Basic Logging** - Difficult to debug production issues

**Low Risk:**
1. **Neo4j Optional** - Already designed as optional feature
2. **External API Dependencies** - Handled with try/catch

---

## 2. Containerization Strategy

### 2.1 Docker Architecture

```
glossary-app/
├── docker-compose.yml          # Production orchestration
├── docker-compose.dev.yml      # Local development (Neo4j only)
├── Dockerfile.backend          # FastAPI container
├── Dockerfile.frontend         # React production build
├── nginx/
│   ├── Dockerfile             # Nginx reverse proxy
│   └── nginx.conf             # Proxy configuration
└── .dockerignore              # Exclude unnecessary files
```

### 2.2 Backend Dockerfile

**File:** `Dockerfile.backend`

```dockerfile
# Multi-stage build for smaller image
FROM python:3.10-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Production stage
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/backend ./src/backend
COPY src/__init__.py ./src/

# Create directories for data persistence
RUN mkdir -p /app/data/uploads /app/data/iate /app/backups

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "src.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.3 Frontend Dockerfile

**File:** `Dockerfile.frontend`

```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY src/frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY src/frontend/ .

# Build production bundle
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 2.4 Nginx Configuration

**File:** `nginx/nginx.conf`

```nginx
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### 2.5 Docker Compose Production

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: glossary-backend
    restart: unless-stopped
    env_file:
      - .env.production
    volumes:
      - ./data:/app/data
      - ./backups:/app/backups
    networks:
      - glossary-network
    depends_on:
      - postgres
      - neo4j
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: glossary-frontend
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - glossary-network
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro  # SSL certificates

  postgres:
    image: postgres:15-alpine
    container_name: glossary-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: glossary
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups/postgres:/backups
    networks:
      - glossary-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5-community
    container_name: glossary-neo4j
    restart: unless-stopped
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_memory_heap_max__size: 2G
      NEO4J_dbms_memory_pagecache_size: 1G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - ./backups/neo4j:/backups
    networks:
      - glossary-network
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${NEO4J_PASSWORD}", "RETURN 1"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  neo4j_data:
  neo4j_logs:

networks:
  glossary-network:
    driver: bridge
```

### 2.6 Environment Variable Management

**Production Secrets:**
- Use Docker secrets or environment variable injection
- Never commit `.env.production` to Git
- Use CI/CD secret management (GitHub Secrets)

**File:** `.env.production.example`

```bash
# Database (PostgreSQL in production)
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/glossary

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=${NEO4J_PASSWORD}

# External APIs
DEEPL_API_KEY=${DEEPL_API_KEY}

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=https://yourdomain.com

# Production Settings
DEBUG=False
LOG_LEVEL=INFO

# Upload limits
MAX_FILE_SIZE_MB=50
```

### 2.7 .dockerignore

**File:** `.dockerignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Development
.git/
.github/
.vscode/
.pytest_cache/
test-screenshots/
test-data/

# Documentation
docs/
*.md
!README.md

# Data (mount as volumes)
data/
backups/
*.db

# Environment files
.env
.env.*
!.env.example
!.env.production.example
```

---

## 3. CI/CD Pipeline

### 3.1 GitHub Actions Workflow

**File:** `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master]

env:
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ghcr.io/${{ github.repository }}/backend
  IMAGE_FRONTEND: ghcr.io/${{ github.repository }}/frontend

jobs:
  # ========== Backend Testing ==========
  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          python -m spacy download en_core_web_sm

      - name: Run pytest
        run: |
          pytest tests/ -v --cov=src/backend --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: backend

  # ========== Frontend Testing ==========
  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: src/frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd src/frontend
          npm ci

      - name: Run tests
        run: |
          cd src/frontend
          npm test -- --coverage --watchAll=false

      - name: Build frontend
        run: |
          cd src/frontend
          npm run build

  # ========== Security Scanning ==========
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # ========== Build Docker Images ==========
  build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, security-scan]
    if: github.event_name == 'push'

    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_BACKEND }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Extract metadata for frontend
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_FRONTEND }}

      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.frontend
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ========== Deploy to Staging ==========
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.yourdomain.com

    steps:
      - name: Deploy to staging server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/glossary-app
            docker-compose pull
            docker-compose up -d
            docker-compose exec -T backend alembic upgrade head

  # ========== Deploy to Production ==========
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/master'
    environment:
      name: production
      url: https://yourdomain.com

    steps:
      - name: Deploy to production server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            cd /opt/glossary-app
            docker-compose pull
            docker-compose up -d
            docker-compose exec -T backend alembic upgrade head

      - name: Health check
        run: |
          sleep 30
          curl -f https://yourdomain.com/health || exit 1
```

### 3.2 Branch Protection Rules

**Configure in GitHub repository settings:**

**Master Branch:**
- Require pull request reviews (1 approval)
- Require status checks to pass (all CI tests)
- Require branches to be up to date
- Restrict who can push (admins only)

**Develop Branch:**
- Require status checks to pass
- Allow force pushes (for rebasing)

### 3.3 Automated Testing Strategy

**Test Levels:**

1. **Unit Tests** (Fast, run on every commit)
   - Backend: pytest (models, services, utilities)
   - Frontend: Jest (components, utilities)
   - Target: 80% code coverage

2. **Integration Tests** (Medium speed)
   - API endpoint tests
   - Database interaction tests
   - External API mocking

3. **End-to-End Tests** (Slow, run on PR only)
   - Cypress tests for critical user flows
   - Upload → Extract → Validate → Export workflow

**Test Matrix:**
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    node-version: ['18', '20']
```

### 3.4 Rollback Strategy

**Automated Rollback:**
```yaml
- name: Deploy with rollback
  run: |
    docker-compose up -d || docker-compose down && docker-compose up -d --force-recreate
```

**Manual Rollback:**
```bash
# SSH to server
ssh production-server

# Revert to previous image
cd /opt/glossary-app
docker-compose down
docker-compose up -d --force-recreate --no-deps --build backend

# Or rollback database migration
docker-compose exec backend alembic downgrade -1
```

---

## 4. Infrastructure & Hosting

### 4.1 Hosting Recommendations

**Option 1: DigitalOcean App Platform (Recommended for MVP)**

**Pros:**
- Managed platform (auto-scaling, monitoring)
- Built-in SSL certificates
- Database managed service (PostgreSQL)
- Easy deployment from GitHub
- Cost-effective ($12-30/month start)

**Cons:**
- Less control than VPS
- Limited customization

**Estimated Cost:**
- Basic Plan: $12/month (backend + frontend)
- Database: $15/month (managed PostgreSQL)
- Total: ~$27/month

**Deployment:**
```bash
# Install doctl CLI
doctl apps create --spec .do/app.yaml

# Or use GitHub integration (recommended)
# Connect repo in DigitalOcean dashboard
```

---

**Option 2: AWS EC2 + RDS (Scalable Production)**

**Pros:**
- Full control over infrastructure
- Scalable (load balancing, auto-scaling)
- Enterprise features (VPC, IAM, CloudWatch)
- PostgreSQL RDS with automated backups

**Cons:**
- More complex setup
- Higher cost
- Requires DevOps expertise

**Estimated Cost:**
- EC2 t3.small: $15/month (1 instance)
- RDS db.t3.micro: $15/month (PostgreSQL)
- Load Balancer: $18/month
- S3 storage: $5/month (PDFs)
- Total: ~$53/month

**Architecture:**
```
┌─────────────┐
│   Route 53  │ (DNS)
└──────┬──────┘
       │
┌──────▼──────────┐
│ Application LB  │ (HTTPS termination)
└──────┬──────────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼──┐
│ EC2 │  │ EC2 │ (Auto-scaling)
└──┬──┘  └──┬──┘
   │        │
   └────┬───┘
        │
   ┌────▼────┐
   │ RDS PG  │ (Multi-AZ)
   └─────────┘
```

---

**Option 3: Self-Hosted VPS (Budget Option)**

**Providers:**
- Hetzner Cloud (€4.15/month - 2 vCPU, 4GB RAM)
- Linode ($12/month - 2GB RAM)
- Vultr ($6/month - 1 vCPU, 2GB RAM)

**Pros:**
- Full control
- Very cost-effective
- Simple for small scale

**Cons:**
- Manual management
- No managed database backups
- You handle security updates

**Setup:**
```bash
# Initial server setup
apt update && apt upgrade -y
apt install docker.io docker-compose nginx certbot

# Clone repository
git clone https://github.com/your-repo/glossary-app.git
cd glossary-app

# Configure environment
cp .env.production.example .env.production
nano .env.production  # Edit secrets

# Start services
docker-compose up -d

# Setup SSL with Let's Encrypt
certbot --nginx -d yourdomain.com
```

---

### 4.2 Database Migration (SQLite → PostgreSQL)

**Why Migrate:**
- SQLite: Single-file, no concurrent writes, no replication
- PostgreSQL: ACID compliant, concurrent access, backups, replication

**Migration Steps:**

1. **Install PostgreSQL client:**
```bash
pip install psycopg2-binary
```

2. **Update DATABASE_URL in .env.production:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/glossary
```

3. **Run Alembic migration:**
```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

4. **Migrate existing data (if any):**
```python
# scripts/migrate_sqlite_to_postgres.py
import sqlite3
import psycopg2

# Export from SQLite
sqlite_conn = sqlite3.connect('data/glossary.db')
# Import to PostgreSQL
pg_conn = psycopg2.connect(DATABASE_URL)
# ... migration logic
```

### 4.3 File Storage for PDFs

**Local Development:** Filesystem (`./data/uploads`)

**Production Options:**

**Option A: AWS S3 (Recommended)**
```python
# Add boto3 to requirements.txt
import boto3

s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)

# Upload file
s3_client.upload_file('document.pdf', 'glossary-bucket', 'uploads/document.pdf')

# Generate presigned URL for temporary access
url = s3_client.generate_presigned_url('get_object',
    Params={'Bucket': 'glossary-bucket', 'Key': 'uploads/document.pdf'},
    ExpiresIn=3600
)
```

**Option B: DigitalOcean Spaces (S3-compatible)**
- Same API as S3
- More affordable ($5/month for 250GB)

**Option C: Local storage with NFS**
- Mount shared volume across containers
- Backup with rsync

### 4.4 SSL/HTTPS Setup

**Option 1: Let's Encrypt (Free)**
```bash
# Install certbot
apt install certbot python3-certbot-nginx

# Generate certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured)
systemctl status certbot.timer
```

**Option 2: Managed Platform (DigitalOcean/AWS)**
- Automatic SSL provisioning
- Certificate renewal handled

**Nginx SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 5. Monitoring & Observability

### 5.1 Application Logging

**Current State:** Basic Python logging to console

**Production Requirements:**

**Structured Logging with JSON:**
```python
# src/backend/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure in app.py
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

**Log Aggregation Options:**

1. **ELK Stack (Self-hosted)**
   - Elasticsearch + Logstash + Kibana
   - Free, powerful search and visualization
   - Requires 4GB+ RAM

2. **Loki + Grafana (Lightweight)**
   - Like Prometheus for logs
   - Lower resource usage
   - Better for smaller deployments

3. **Cloud-based (Managed)**
   - Datadog ($15/host/month)
   - Logtail ($9/month)
   - Better.Stack ($10/month)

**Docker Logging Configuration:**
```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=backend"
```

### 5.2 Performance Monitoring

**Application Performance Monitoring (APM):**

**Option 1: Sentry (Recommended for Errors)**
```bash
pip install sentry-sdk[fastapi]
```

```python
# src/backend/app.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    environment="production"
)
```

**Pricing:** Free tier (5,000 events/month), then $26/month

**Option 2: Prometheus + Grafana (Self-hosted)**
```python
# Add prometheus client
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

**Grafana Dashboard:**
- Request rate, error rate, duration
- Database query performance
- Memory/CPU usage

### 5.3 Health Check Monitoring

**Uptime Monitoring Services:**

1. **UptimeRobot (Free)**
   - 50 monitors free
   - 5-minute interval checks
   - Email/SMS alerts

2. **Better Uptime ($10/month)**
   - Status page included
   - Multiple locations
   - Faster checks (30s)

3. **Healthchecks.io (Free)**
   - Cron job monitoring
   - API endpoints

**Configuration:**
```python
# Enhanced /health endpoint
@app.get("/health")
async def health_check():
    checks = {
        "database": check_database(),
        "neo4j": check_neo4j(),
        "disk_space": check_disk_space(),
        "memory": check_memory()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### 5.4 Database Backups

**Automated Backup Strategy:**

**PostgreSQL Backups:**
```bash
# scripts/backup-postgres.sh
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/glossary_$TIMESTAMP.sql.gz"

docker-compose exec -T postgres pg_dump -U $POSTGRES_USER glossary | gzip > $BACKUP_FILE

# Retention: Keep last 7 daily, 4 weekly, 6 monthly
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

**Cron Schedule:**
```cron
# Daily backup at 2 AM
0 2 * * * /opt/glossary-app/scripts/backup-postgres.sh

# Weekly Neo4j backup (Sunday 3 AM)
0 3 * * 0 /opt/glossary-app/scripts/backup-neo4j.sh
```

**Backup to Cloud Storage:**
```bash
# Sync to S3
aws s3 sync /backups s3://glossary-backups/ --storage-class STANDARD_IA
```

**Neo4j Backups:**
```bash
# scripts/backup-neo4j.sh
docker-compose exec neo4j neo4j-admin database dump neo4j \
  --to-path=/backups/neo4j_$(date +%Y%m%d).dump
```

### 5.5 Alerting Strategy

**Alert Channels:**
- Email (critical errors)
- Slack/Discord webhook (warnings)
- PagerDuty (production outages, on-call)

**Alert Rules:**

**Critical (Immediate Action):**
- API downtime > 1 minute
- Database connection failures
- Disk space < 10%
- Memory usage > 90%

**Warning (Within 1 hour):**
- Error rate > 5% of requests
- Response time > 2 seconds (95th percentile)
- Failed backup jobs

**Info (Monitor):**
- New deployments
- Scheduled maintenance
- Unusual traffic patterns

---

## 6. Implementation Timeline

### 6.1 Week 3-4: MVP Production Deploy

**Goal:** Get a working production deployment with minimal features

**Tasks:**

**Week 3:**
- [ ] Create Dockerfiles (backend, frontend, nginx)
- [ ] Set up docker-compose.yml for production
- [ ] Migrate database from SQLite to PostgreSQL
- [ ] Configure Alembic for database migrations
- [ ] Set up basic CI pipeline (test + build)
- [ ] Choose hosting platform (DigitalOcean recommended)

**Week 4:**
- [ ] Deploy to production server
- [ ] Configure SSL with Let's Encrypt
- [ ] Set up basic monitoring (UptimeRobot)
- [ ] Configure automated backups (daily PostgreSQL dump)
- [ ] Create deployment documentation
- [ ] Perform smoke tests on production

**Deliverables:**
- Working HTTPS production site
- Automated deployments from master branch
- Daily database backups
- Basic uptime monitoring

**Effort:** 20-30 hours

---

### 6.2 Month 2: Improved Infrastructure

**Goal:** Enhance CI/CD, monitoring, and operational reliability

**Tasks:**

**Week 5-6:**
- [ ] Implement comprehensive CI/CD pipeline
  - [ ] Automated testing (unit, integration, E2E)
  - [ ] Security scanning (Trivy)
  - [ ] Code coverage reporting
  - [ ] Branch protection rules
- [ ] Set up staging environment
- [ ] Implement blue-green deployment strategy

**Week 7-8:**
- [ ] Add application monitoring (Sentry for errors)
- [ ] Set up structured logging (JSON format)
- [ ] Create Grafana dashboards for metrics
- [ ] Implement rate limiting on API endpoints
- [ ] Add API key management for external services
- [ ] Document rollback procedures

**Deliverables:**
- Full CI/CD pipeline with staging
- Error tracking and alerting
- Performance metrics dashboard
- Security hardening

**Effort:** 30-40 hours

---

### 6.3 Month 3: Scaling & Optimization

**Goal:** Prepare for growth and optimize performance

**Tasks:**

**Week 9-10:**
- [ ] Migrate file storage to S3/Spaces
- [ ] Implement CDN for static assets (CloudFlare)
- [ ] Add database connection pooling
- [ ] Optimize database queries (indexes, EXPLAIN ANALYZE)
- [ ] Implement caching layer (Redis)

**Week 11-12:**
- [ ] Set up load balancing (if using AWS/custom VPS)
- [ ] Configure auto-scaling rules
- [ ] Implement disaster recovery plan
- [ ] Create runbooks for common incidents
- [ ] Performance testing and optimization
- [ ] Documentation updates

**Deliverables:**
- Scalable infrastructure
- Sub-second API response times
- Disaster recovery plan
- Complete operational documentation

**Effort:** 30-40 hours

---

### 6.4 Quick Reference Timeline

| Phase | Duration | Key Outcome | Investment |
|-------|----------|-------------|------------|
| **MVP Deploy** | Week 3-4 | Production site live | 20-30h |
| **Enhanced Infra** | Month 2 | Full CI/CD + Monitoring | 30-40h |
| **Scaling** | Month 3 | Optimized & Scalable | 30-40h |
| **Total** | ~3 months | Production-ready platform | 80-110h |

---

## 7. Security Checklist

### 7.1 Pre-Production Security

**Required Before Launch:**

- [ ] All secrets moved to environment variables (no hardcoded values)
- [ ] .env files excluded from Git (.gitignore configured)
- [ ] HTTPS/SSL configured (Let's Encrypt)
- [ ] CORS restricted to production domain only
- [ ] Database credentials rotated (not using defaults)
- [ ] Neo4j password changed from default
- [ ] DeepL API key secured
- [ ] File upload size limits enforced (50MB)
- [ ] File type validation (only PDF, DOCX, Excel)
- [ ] SQL injection prevention (using ORM parameterization)
- [ ] XSS protection (Content Security Policy headers)
- [ ] CSRF tokens for state-changing operations

### 7.2 Ongoing Security

**Monthly:**
- [ ] Dependency updates (npm audit, pip-audit)
- [ ] Security patch review
- [ ] SSL certificate renewal check (auto-renewed)

**Quarterly:**
- [ ] Penetration testing (basic)
- [ ] Access log review
- [ ] Backup restoration test

**Annually:**
- [ ] Full security audit
- [ ] Credential rotation (database passwords, API keys)

### 7.3 Security Scanning

**Automated Scans in CI/CD:**

```yaml
# .github/workflows/security.yml
- name: Python dependency scan
  run: |
    pip install safety
    safety check --json

- name: JavaScript dependency scan
  run: |
    npm audit --audit-level=moderate

- name: Container image scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/your-repo/backend:latest'
```

---

## 8. Cost Estimates

### 8.1 Option 1: DigitalOcean (Recommended for MVP)

| Service | Specification | Monthly Cost |
|---------|--------------|--------------|
| App Platform | Basic (1 container) | $12 |
| Managed PostgreSQL | Basic (1GB RAM) | $15 |
| Spaces (S3-compatible) | 250GB storage | $5 |
| Monitoring (UptimeRobot) | Free tier | $0 |
| SSL Certificate | Let's Encrypt | $0 |
| **Total** | | **$32/month** |

**Annual:** $384

---

### 8.2 Option 2: AWS (Production Scale)

| Service | Specification | Monthly Cost |
|---------|--------------|--------------|
| EC2 | t3.small (2 vCPU, 2GB) | $15 |
| RDS PostgreSQL | db.t3.micro | $15 |
| Application Load Balancer | 1 ALB | $18 |
| S3 Storage | 100GB + requests | $5 |
| CloudWatch Logs | 5GB ingestion | $3 |
| Route 53 | DNS hosting | $1 |
| **Total** | | **$57/month** |

**Annual:** $684

**With scaling (2 EC2 instances):** $87/month

---

### 8.3 Option 3: Self-Hosted VPS

| Service | Specification | Monthly Cost |
|---------|--------------|--------------|
| Hetzner Cloud VPS | CX21 (2 vCPU, 4GB RAM) | €4.15 (~$4.50) |
| Backups (Hetzner) | Automated snapshots | €0.83 (~$1) |
| Domain Name | .com registration | $1 (annually $12) |
| SSL Certificate | Let's Encrypt | $0 |
| Monitoring (UptimeRobot) | Free tier | $0 |
| **Total** | | **$5.50/month** |

**Annual:** $66

**Note:** Requires more manual DevOps work

---

### 8.4 Additional Costs (Optional)

| Service | Purpose | Monthly Cost |
|---------|---------|--------------|
| Sentry | Error tracking | $26 (team plan) |
| Better Uptime | Advanced monitoring | $10 |
| Datadog | Full observability | $15/host |
| GitHub Actions | CI/CD (>2000 min) | $0-8 |
| **Optional Total** | | **$51/month** |

---

### 8.5 Recommended Starting Point

**For MVP (Months 1-3):**
- **Platform:** DigitalOcean App Platform
- **Cost:** $32/month
- **Includes:** Hosting, database, file storage, SSL

**After Product-Market Fit:**
- **Migrate to:** AWS or self-hosted
- **Add:** Advanced monitoring, CDN
- **Cost:** $60-100/month

---

## 9. Next Steps

### 9.1 Immediate Actions (This Week)

1. **Create Dockerfiles**
   ```bash
   touch Dockerfile.backend Dockerfile.frontend
   mkdir nginx
   touch nginx/nginx.conf
   ```

2. **Set up GitHub Actions**
   ```bash
   mkdir -p .github/workflows
   touch .github/workflows/ci-cd.yml
   ```

3. **Choose hosting provider**
   - Sign up for DigitalOcean (recommended)
   - Or set up AWS free tier account

4. **Configure Alembic for migrations**
   ```bash
   alembic init alembic
   # Edit alembic.ini and env.py
   ```

### 9.2 Week 3 Sprint Plan

**Day 1-2:** Containerization
- Write Dockerfiles
- Test local Docker builds
- Create docker-compose.yml

**Day 3-4:** Database Migration
- Set up PostgreSQL locally
- Configure Alembic
- Test migration scripts

**Day 5:** CI/CD Setup
- Create GitHub Actions workflow
- Configure secrets in GitHub

**Weekend:** Production Deployment
- Deploy to hosting platform
- Configure DNS and SSL
- Smoke testing

### 9.3 Getting Help

**Questions to ask before starting:**
- Do you have a domain name ready?
- What's your expected user load? (affects hosting choice)
- Do you need Neo4j in production immediately? (adds complexity)
- Budget constraints? (affects platform choice)

**Resources:**
- Docker documentation: https://docs.docker.com
- DigitalOcean tutorials: https://www.digitalocean.com/community/tutorials
- GitHub Actions docs: https://docs.github.com/actions
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/

---

## Summary

**Current State:**
- Code is production-ready (security, error handling, logging)
- Missing deployment infrastructure

**Recommended Path:**
1. **Week 3-4:** Dockerize + Deploy to DigitalOcean ($32/month)
2. **Month 2:** Add CI/CD + monitoring
3. **Month 3:** Optimize and scale

**Fastest MVP:**
- Use DigitalOcean App Platform (managed)
- Skip Neo4j initially (optional feature)
- Use managed PostgreSQL (no backup automation needed)
- Let's Encrypt for SSL (automatic)
- UptimeRobot for basic monitoring (free)

**Total time to production:** 2-3 weeks (20-30 hours)

**Total initial cost:** $32/month

---

**Ready to proceed?** Start with creating the Dockerfiles and testing locally!

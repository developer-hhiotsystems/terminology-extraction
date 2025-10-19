# Production Deployment Checklist

## Pre-Deployment Checklist

### ✅ Code Quality
- [ ] All code committed to version control
- [ ] No sensitive data (API keys, passwords) in code
- [ ] Environment variables configured
- [ ] Dependencies locked (requirements.txt, package-lock.json)
- [ ] TypeScript compilation successful
- [ ] No console.log statements in production code
- [ ] Error handling implemented for all API calls

### ✅ Database
- [ ] Database migrations tested
- [ ] FTS5 index initialized
- [ ] Backup strategy in place
- [ ] Database connection pooling configured
- [ ] Foreign key constraints verified
- [ ] Indexes optimized for queries

### ✅ Backend API
- [ ] Health check endpoint working
- [ ] CORS configured correctly
- [ ] Rate limiting implemented
- [ ] Request validation in place
- [ ] Error logging configured
- [ ] API documentation up to date
- [ ] Authentication/authorization (if required)

### ✅ Frontend
- [ ] Production build tested
- [ ] Environment variables set
- [ ] API endpoints configured
- [ ] Error boundaries implemented
- [ ] Loading states for all async operations
- [ ] 404 and error pages created
- [ ] Assets optimized (images, fonts)

### ✅ Security
- [ ] HTTPS enabled
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection (React handles this)
- [ ] CSRF protection (if using cookies)
- [ ] Input validation on all forms
- [ ] File upload size limits
- [ ] Security headers configured

### ✅ Performance
- [ ] FTS5 search tested with large datasets
- [ ] Frontend bundle size optimized
- [ ] Images compressed and optimized
- [ ] Database queries optimized
- [ ] Caching strategy implemented
- [ ] CDN configured (if applicable)

### ✅ Monitoring
- [ ] Health monitoring endpoint
- [ ] Error tracking configured
- [ ] Performance metrics collected
- [ ] Log aggregation setup
- [ ] Uptime monitoring
- [ ] Alert notifications configured

### ✅ Backup & Recovery
- [ ] Automated database backups
- [ ] Backup verification process
- [ ] Recovery procedure documented
- [ ] Backup retention policy defined
- [ ] Off-site backup storage

### ✅ Documentation
- [ ] API documentation complete
- [ ] User guide created
- [ ] Admin guide created
- [ ] Troubleshooting guide
- [ ] Architecture documentation
- [ ] Deployment runbook

---

## Deployment Steps

### 1. Prepare Environment

```bash
# Create production directory
mkdir -p /var/www/glossary-app
cd /var/www/glossary-app

# Clone repository
git clone <repository-url> .

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Install frontend dependencies
cd src/frontend
npm ci --production
```

### 2. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit with production values
nano .env
```

**.env Example:**
```env
# Database
DATABASE_URL=sqlite:///data/glossary.db

# API
API_HOST=0.0.0.0
API_PORT=9123
API_WORKERS=4

# Frontend
REACT_APP_API_URL=https://api.yourglossary.com

# Security
SECRET_KEY=<generate-secure-random-key>
ALLOWED_ORIGINS=https://yourglossary.com

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=<your-sentry-dsn>

# Backups
BACKUP_DIR=/var/backups/glossary
BACKUP_RETENTION_DAYS=30
```

### 3. Initialize Database

```bash
# Create data directory
mkdir -p data

# Apply schema
sqlite3 data/glossary.db < src/backend/database_schema_update.sql

# Initialize FTS5
python scripts/initialize_fts5.py

# Extract relationships (if needed)
python scripts/batch_extract_relationships.py
```

### 4. Build Frontend

```bash
cd src/frontend

# Build production bundle
npm run build

# Test build locally
npm run preview
```

### 5. Configure Web Server

#### Option A: Nginx (Recommended)

```nginx
# /etc/nginx/sites-available/glossary-app

server {
    listen 80;
    server_name yourglossary.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourglossary.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourglossary.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourglossary.com/privkey.pem;

    # Frontend (React app)
    location / {
        root /var/www/glossary-app/src/frontend/dist;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API (proxy to FastAPI)
    location /api/ {
        proxy_pass http://127.0.0.1:9123;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Rate limiting
    limit_req zone=api_limit burst=20 nodelay;
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
```

#### Option B: Apache

```apache
# /etc/apache2/sites-available/glossary-app.conf

<VirtualHost *:80>
    ServerName yourglossary.com
    Redirect permanent / https://yourglossary.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName yourglossary.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/yourglossary.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/yourglossary.com/privkey.pem

    # Frontend
    DocumentRoot /var/www/glossary-app/src/frontend/dist

    <Directory /var/www/glossary-app/src/frontend/dist>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted

        # React Router support
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    # Backend API proxy
    ProxyPreserveHost On
    ProxyPass /api/ http://127.0.0.1:9123/api/
    ProxyPassReverse /api/ http://127.0.0.1:9123/api/
</VirtualHost>
```

### 6. Setup Process Manager

#### Using systemd (Linux)

```ini
# /etc/systemd/system/glossary-api.service

[Unit]
Description=Glossary App API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/glossary-app
Environment="PATH=/var/www/glossary-app/venv/bin"
ExecStart=/var/www/glossary-app/venv/bin/uvicorn src.backend.app:app --host 0.0.0.0 --port 9123 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable glossary-api
sudo systemctl start glossary-api
sudo systemctl status glossary-api
```

#### Using PM2 (Node.js)

```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start "venv/bin/uvicorn src.backend.app:app --host 0.0.0.0 --port 9123 --workers 4" --name glossary-api

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

### 7. Configure Monitoring

```bash
# Install monitoring tools
pip install sentry-sdk python-dotenv

# Setup log rotation
sudo nano /etc/logrotate.d/glossary-app
```

**Log rotation config:**
```
/var/www/glossary-app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload glossary-api > /dev/null 2>&1 || true
    endscript
}
```

### 8. Setup Automated Backups

```bash
# Create backup directory
sudo mkdir -p /var/backups/glossary
sudo chown www-data:www-data /var/backups/glossary

# Add backup script to cron
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /var/www/glossary-app/scripts/backup_database.sh
```

### 9. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourglossary.com

# Auto-renewal (certbot adds this automatically)
# Verify renewal works
sudo certbot renew --dry-run
```

### 10. Verify Deployment

```bash
# Test health endpoint
curl https://yourglossary.com/health

# Test API
curl https://yourglossary.com/api/glossary?limit=5

# Test search
curl https://yourglossary.com/api/search/fulltext?q=temperature

# Test frontend
curl https://yourglossary.com/
```

---

## Post-Deployment

### ✅ Verification Tests
- [ ] Health check returns 200
- [ ] API endpoints responding
- [ ] Frontend loads correctly
- [ ] Search functionality works
- [ ] Database queries executing
- [ ] Relationships displaying
- [ ] File uploads working

### ✅ Performance Tests
- [ ] Load testing completed
- [ ] Response times acceptable (< 200ms)
- [ ] Concurrent users tested
- [ ] Memory usage stable
- [ ] CPU usage reasonable

### ✅ Security Tests
- [ ] HTTPS working
- [ ] Security headers present
- [ ] CORS configured correctly
- [ ] No exposed sensitive data
- [ ] Rate limiting functional

### ✅ Monitoring Setup
- [ ] Error tracking active
- [ ] Logs collecting
- [ ] Alerts configured
- [ ] Uptime monitoring
- [ ] Performance metrics

### ✅ Backup Verification
- [ ] First backup completed
- [ ] Backup restoration tested
- [ ] Backup size reasonable
- [ ] Off-site storage working

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Stop services
sudo systemctl stop glossary-api
sudo systemctl stop nginx

# 2. Restore previous version
cd /var/www/glossary-app
git checkout <previous-commit>

# 3. Restore database from backup
cp /var/backups/glossary/latest/glossary.db data/glossary.db

# 4. Restart services
sudo systemctl start nginx
sudo systemctl start glossary-api

# 5. Verify rollback
curl https://yourglossary.com/health
```

---

## Maintenance Windows

Schedule regular maintenance:

- **Daily:** Automated backups at 2 AM
- **Weekly:** Log review and cleanup
- **Monthly:** Security updates
- **Quarterly:** Full system audit

---

## Support Contacts

- **Technical Lead:** [Your Name]
- **DevOps:** [DevOps Contact]
- **Emergency:** [Emergency Contact]

---

## Additional Resources

- [Production Monitoring Guide](PRODUCTION_MONITORING.md)
- [Backup & Recovery Guide](BACKUP_RECOVERY.md)
- [Security Best Practices](SECURITY_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

**Last Updated:** 2025-10-19
**Version:** 1.0.0
**Status:** Production Ready ✅

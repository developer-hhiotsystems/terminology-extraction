# Health Monitoring System Guide

## Overview

The Glossary App includes a comprehensive health monitoring system that provides real-time visibility into application health, performance, and resource usage. This system is essential for production deployments, enabling proactive monitoring and quick incident response.

---

## Architecture

### Components

1. **HealthChecker** (`src/backend/monitoring/health_check.py`)
   - Core health checking logic
   - Monitors all subsystems
   - Provides simple and detailed health status

2. **Health API Router** (`src/backend/routers/health.py`)
   - REST API endpoints for health checks
   - Kubernetes-compatible readiness/liveness probes
   - Performance metrics endpoint

3. **Performance Tracker Middleware** (`src/backend/middleware/performance_tracker.py`)
   - Tracks request/response times
   - Feeds data to health checker
   - Adds timing headers to responses

---

## Health Check Endpoints

### 1. Simple Health Check
**Endpoint:** `GET /health`

Quick health check suitable for load balancers and uptime monitoring.

**Response (Healthy):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T10:30:00.000Z"
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "error": "Database connection failed",
  "timestamp": "2025-10-19T10:30:00.000Z"
}
```

**HTTP Status Codes:**
- `200 OK` - System is healthy
- `503 Service Unavailable` - System is unhealthy

**Usage:**
```bash
# cURL
curl http://localhost:9123/health

# Health check in monitoring tool
wget -q --spider http://localhost:9123/health
```

---

### 2. Detailed Health Check
**Endpoint:** `GET /health/detailed`

Comprehensive health status covering all subsystems.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T10:30:00.000Z",
  "version": "1.0.0",
  "check_duration_ms": 45.23,
  "subsystems": {
    "database": {
      "status": "healthy",
      "entry_count": 3312,
      "database_size_mb": 45.67,
      "integrity": "ok",
      "active_connections": 1,
      "database_path": "data/glossary.db",
      "issues": []
    },
    "fts_search": {
      "status": "healthy",
      "fts_enabled": true,
      "indexed_entries": 3312,
      "main_entries": 3312,
      "sync_status": "synchronized",
      "search_performance_ms": 12.34,
      "issues": []
    },
    "disk": {
      "status": "healthy",
      "free_gb": 125.45,
      "total_gb": 500.00,
      "used_percent": 74.91,
      "path": "data",
      "issues": []
    },
    "memory": {
      "status": "healthy",
      "total_gb": 16.00,
      "available_gb": 8.50,
      "used_percent": 46.88,
      "issues": []
    },
    "backups": {
      "status": "healthy",
      "backup_enabled": true,
      "backup_count": 15,
      "latest_backup": "glossary_backup_20251019_020000.db.gz",
      "backup_age_hours": 8.50,
      "backup_size_mb": 12.34,
      "issues": []
    },
    "performance": {
      "status": "healthy",
      "total_requests": 1542,
      "avg_response_time_ms": 85.67,
      "recent_avg_response_time_ms": 72.34,
      "max_response_time_ms": 450.12,
      "min_response_time_ms": 15.23,
      "issues": []
    }
  },
  "issues": [],
  "healthy": true
}
```

**HTTP Status Codes:**
- `200 OK` - System is healthy or degraded
- `503 Service Unavailable` - System is unhealthy

**Subsystem Statuses:**
- `healthy` - Subsystem operating normally
- `degraded` - Subsystem operational but with warnings
- `unhealthy` - Subsystem has critical issues

---

### 3. Health Metrics
**Endpoint:** `GET /health/metrics`

Summary metrics for monitoring dashboards (Grafana, Datadog, etc.).

**Response:**
```json
{
  "timestamp": "2025-10-19T10:30:00.000Z",
  "overall_status": "healthy",
  "total_requests": 1542,
  "avg_response_time_ms": 85.67,
  "database_entries": 3312,
  "database_size_mb": 45.67,
  "fts_indexed_entries": 3312,
  "disk_free_gb": 125.45,
  "disk_used_percent": 74.91,
  "memory_used_percent": 46.88,
  "memory_available_gb": 8.50,
  "backup_count": 15,
  "backup_age_hours": 8.50,
  "issue_count": 0,
  "issues": []
}
```

**Usage:**
```bash
# Get metrics
curl http://localhost:9123/health/metrics

# Parse with jq
curl -s http://localhost:9123/health/metrics | jq '.avg_response_time_ms'
```

---

### 4. Kubernetes Probes

#### Readiness Probe
**Endpoint:** `GET /health/ready`

Checks if the application is ready to serve traffic.

**Response (Ready):**
```json
{
  "ready": true,
  "message": "Application is ready to serve traffic"
}
```

**Response (Not Ready):**
```json
{
  "ready": false,
  "message": "Application is not ready",
  "database": "unhealthy",
  "fts": "healthy"
}
```

**Kubernetes Configuration:**
```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 9123
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

#### Liveness Probe
**Endpoint:** `GET /health/liveness`

Checks if the application process is alive.

**Response:**
```json
{
  "alive": true,
  "message": "Application process is alive"
}
```

**Kubernetes Configuration:**
```yaml
livenessProbe:
  httpGet:
    path: /health/liveness
    port: 9123
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3
```

#### Ping
**Endpoint:** `GET /health/ping`

Ultra-simple connectivity test.

**Response:**
```json
{
  "status": "pong",
  "message": "Service is reachable"
}
```

---

## Subsystem Details

### 1. Database Health
Monitors SQLite database connectivity and integrity.

**Checks:**
- ✓ Database file exists and is readable
- ✓ Can execute queries
- ✓ PRAGMA integrity_check passes
- ✓ Entry count available
- ✓ Database size tracking

**Issues:**
- Database file not found
- Connection refused
- Integrity check failed
- Corrupted database

---

### 2. FTS5 Search Health
Monitors full-text search index status.

**Checks:**
- ✓ FTS5 table exists
- ✓ Index synchronized with main table
- ✓ Search performance acceptable
- ✓ Index size tracking

**Issues:**
- FTS5 index not found
- Count mismatch between FTS and main table
- Slow search performance (> 1 second)

**Auto-fix:**
If FTS is out of sync, run:
```bash
python scripts/initialize_fts5.py
```

---

### 3. Disk Health
Monitors disk space availability.

**Checks:**
- ✓ Free disk space
- ✓ Total disk capacity
- ✓ Used percentage

**Thresholds:**
- **Warning:** < 5 GB free
- **Critical:** < 1 GB free

**Issues:**
- Low disk space warning
- Critical disk space
- Disk full

**Remediation:**
```bash
# Clean old backups
python scripts/backup_database.py --cleanup --retention-days 7

# Compress database
sqlite3 data/glossary.db "VACUUM;"
```

---

### 4. Memory Health
Monitors system memory usage.

**Checks:**
- ✓ Total memory
- ✓ Available memory
- ✓ Used percentage

**Thresholds:**
- **Warning:** > 85% used
- **Critical:** > 95% used

**Issues:**
- High memory usage warning
- Critical memory usage

**Remediation:**
```bash
# Restart application
sudo systemctl restart glossary-api

# Check for memory leaks
top -p $(pgrep -f "glossary-api")
```

---

### 5. Backup Health
Monitors backup status and recency.

**Checks:**
- ✓ Backup directory exists
- ✓ Backups present
- ✓ Latest backup age
- ✓ Backup size

**Thresholds:**
- **Warning:** > 24 hours since last backup
- **Critical:** > 7 days since last backup

**Issues:**
- No backups found
- Backup too old
- Backup directory missing

**Remediation:**
```bash
# Run manual backup
python scripts/backup_database.py --compress --verify

# Check cron job
crontab -l | grep backup_database
```

---

### 6. Performance Health
Monitors API request/response times.

**Checks:**
- ✓ Average response time
- ✓ Recent response time trend
- ✓ Maximum response time
- ✓ Total request count

**Thresholds:**
- **Warning:** > 500ms average
- **Critical:** > 2000ms average

**Issues:**
- Slow average response time
- Performance degradation

**Remediation:**
```bash
# Check slow queries
sqlite3 data/glossary.db "EXPLAIN QUERY PLAN SELECT * FROM glossary_entries_fts WHERE glossary_entries_fts MATCH 'temperature';"

# Rebuild FTS5 index
python scripts/initialize_fts5.py

# Check system resources
htop
```

---

## Integration with App

### Step 1: Add Health Router to App

Edit `src/backend/app.py`:

```python
from routers.health import router as health_router

# Add health router
app.include_router(health_router)
```

### Step 2: Add Performance Tracking Middleware

Edit `src/backend/app.py`:

```python
from middleware.performance_tracker import PerformanceTrackerMiddleware

# Add performance tracking
app.add_middleware(PerformanceTrackerMiddleware)
```

### Step 3: Install Dependencies

```bash
venv\Scripts\activate
pip install psutil
```

### Step 4: Test Health Endpoints

```bash
# Start backend
venv\Scripts\python.exe src\backend\app.py

# Test simple health
curl http://localhost:9123/health

# Test detailed health
curl http://localhost:9123/health/detailed

# Test metrics
curl http://localhost:9123/health/metrics
```

---

## Monitoring Integration

### 1. Uptime Monitoring (UptimeRobot, Pingdom)

**Configuration:**
- **URL:** `https://yourglossary.com/health`
- **Method:** GET
- **Expected Status:** 200
- **Check Interval:** 5 minutes
- **Alert:** Email/SMS on failure

---

### 2. Prometheus

**Scrape Configuration:**
```yaml
scrape_configs:
  - job_name: 'glossary-api'
    metrics_path: '/health/metrics'
    static_configs:
      - targets: ['yourglossary.com:9123']
```

**Custom Exporter (Optional):**
Create a Prometheus exporter that parses `/health/metrics`:

```python
# metrics_exporter.py
from prometheus_client import Gauge, generate_latest
import requests

response_time = Gauge('glossary_avg_response_time_ms', 'Average response time')
database_entries = Gauge('glossary_database_entries', 'Total database entries')
# ... more metrics

metrics = requests.get('http://localhost:9123/health/metrics').json()
response_time.set(metrics['avg_response_time_ms'])
database_entries.set(metrics['database_entries'])
```

---

### 3. Grafana Dashboard

**Queries:**
```sql
-- Average Response Time
avg_over_time(glossary_avg_response_time_ms[5m])

-- Database Growth
rate(glossary_database_entries[1h])

-- Disk Usage
glossary_disk_used_percent

-- Memory Usage
glossary_memory_used_percent
```

**Alerts:**
- Response time > 500ms for 5 minutes
- Disk free < 5 GB
- Memory usage > 85%
- Backup age > 24 hours

---

### 4. Datadog / New Relic

**HTTP Check:**
- **URL:** `https://yourglossary.com/health/detailed`
- **Parse JSON:** Extract metrics from response
- **Create Dashboards:** Visualize metrics
- **Setup Alerts:** Notify on issues

---

### 5. Nagios / Icinga

**Check Command:**
```bash
#!/bin/bash
# check_glossary_health.sh

RESPONSE=$(curl -s http://localhost:9123/health/detailed)
STATUS=$(echo $RESPONSE | jq -r '.status')

if [ "$STATUS" == "healthy" ]; then
  echo "OK - Glossary API is healthy"
  exit 0
elif [ "$STATUS" == "degraded" ]; then
  echo "WARNING - Glossary API is degraded"
  exit 1
else
  echo "CRITICAL - Glossary API is unhealthy"
  exit 2
fi
```

---

## Troubleshooting

### Issue: FTS Count Mismatch

**Symptom:**
```json
{
  "fts_search": {
    "status": "degraded",
    "sync_status": "out_of_sync",
    "issues": ["FTS5 count mismatch: 3300 vs 3312 entries"]
  }
}
```

**Solution:**
```bash
python scripts/initialize_fts5.py
```

---

### Issue: Slow Search Performance

**Symptom:**
```json
{
  "fts_search": {
    "search_performance_ms": 2500.00,
    "issues": ["FTS5 search slow: 2500.00ms"]
  }
}
```

**Solutions:**
1. Rebuild FTS5 index:
```bash
python scripts/initialize_fts5.py
```

2. Vacuum database:
```bash
sqlite3 data/glossary.db "VACUUM;"
```

3. Check database size and entries

---

### Issue: Old Backup

**Symptom:**
```json
{
  "backups": {
    "backup_age_hours": 48.50,
    "issues": ["Warning: Last backup is 48.5 hours old"]
  }
}
```

**Solution:**
```bash
# Run manual backup
python scripts/backup_database.py --compress --verify

# Check cron job
crontab -l

# Add cron job (if missing)
crontab -e
# Add: 0 2 * * * /path/to/scripts/backup_database.sh
```

---

### Issue: High Memory Usage

**Symptom:**
```json
{
  "memory": {
    "used_percent": 92.50,
    "issues": ["Warning: High memory usage - 92.5%"]
  }
}
```

**Solutions:**
1. Restart application:
```bash
sudo systemctl restart glossary-api
```

2. Check for memory leaks:
```bash
ps aux | grep python
top -p $(pgrep -f glossary)
```

3. Monitor over time to identify leak patterns

---

## Best Practices

### 1. Regular Monitoring
- Check health endpoints every 5 minutes
- Review detailed health daily
- Monitor trends over time

### 2. Alerting Strategy
- **Critical:** Page on-call engineer (backup age > 7 days, database down)
- **Warning:** Email/Slack notification (disk < 5 GB, memory > 85%)
- **Info:** Log for review (performance degradation)

### 3. Health Check Frequency
- **Simple health:** Every 1-5 minutes (load balancers)
- **Detailed health:** Every 15 minutes (monitoring tools)
- **Metrics:** Every 5 minutes (dashboards)

### 4. Response Time Baselines
Establish baselines for your workload:
- **P50:** 50th percentile response time
- **P95:** 95th percentile response time
- **P99:** 99th percentile response time

Alert when current metrics exceed baseline by 50%.

---

## API Response Time Header

All API requests include a timing header:

```
X-Response-Time: 45.67ms
```

**Usage in client:**
```typescript
const response = await fetch('/api/glossary');
const responseTime = response.headers.get('X-Response-Time');
console.log(`Request took ${responseTime}`);
```

---

## Configuration

Health check thresholds can be customized:

```python
# In src/backend/app.py or config
from monitoring.health_check import HealthChecker

checker = HealthChecker(
    warning_disk_threshold_gb=10.0,      # Warn if < 10 GB free
    critical_disk_threshold_gb=2.0,      # Critical if < 2 GB free
    warning_memory_threshold_percent=80.0,  # Warn if > 80% used
    critical_memory_threshold_percent=90.0  # Critical if > 90% used
)
```

---

## Summary

The health monitoring system provides:

✅ **Comprehensive Health Checks** - Database, FTS, disk, memory, backups, performance
✅ **Multiple Endpoints** - Simple, detailed, metrics, Kubernetes probes
✅ **Production-Ready** - Suitable for load balancers, monitoring tools, dashboards
✅ **Performance Tracking** - Request/response time monitoring
✅ **Issue Detection** - Automatic detection of degraded/unhealthy states
✅ **Easy Integration** - Works with Prometheus, Grafana, Datadog, etc.

**Next Steps:**
1. Integrate health router into app.py
2. Add performance tracking middleware
3. Test all health endpoints
4. Configure monitoring tools
5. Set up alerting
6. Document on-call procedures

---

**Last Updated:** 2025-10-19
**Version:** 1.0.0
**Status:** Production Ready ✅

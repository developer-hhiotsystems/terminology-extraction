"""
Health Monitoring System

Provides comprehensive health checks for production monitoring:
- Database connectivity and integrity
- FTS5 search index status
- System resources (disk, memory)
- Backup status
- API performance metrics

Usage:
    from monitoring.health_check import HealthChecker

    checker = HealthChecker(db_session)
    health_status = checker.get_health_status()
"""

import os
import time
import psutil
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text


class HealthStatus:
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """Comprehensive health checking for the glossary application"""

    def __init__(
        self,
        db_path: str = "data/glossary.db",
        backup_dir: str = "backups",
        warning_disk_threshold_gb: float = 5.0,
        critical_disk_threshold_gb: float = 1.0,
        warning_memory_threshold_percent: float = 85.0,
        critical_memory_threshold_percent: float = 95.0
    ):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.warning_disk_threshold_gb = warning_disk_threshold_gb
        self.critical_disk_threshold_gb = critical_disk_threshold_gb
        self.warning_memory_threshold_percent = warning_memory_threshold_percent
        self.critical_memory_threshold_percent = critical_memory_threshold_percent

        # Performance tracking
        self.request_times: List[float] = []
        self.max_request_history = 1000

    def get_health_status(self, db_session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get comprehensive health status

        Returns:
            dict: Complete health status including all subsystems
        """
        start_time = time.time()

        # Check all subsystems
        db_health = self._check_database_health(db_session)
        fts_health = self._check_fts_health()
        disk_health = self._check_disk_health()
        memory_health = self._check_memory_health()
        backup_health = self._check_backup_health()
        performance_health = self._check_performance_health()

        # Determine overall status
        overall_status = self._determine_overall_status([
            db_health["status"],
            fts_health["status"],
            disk_health["status"],
            memory_health["status"],
            backup_health["status"],
            performance_health["status"]
        ])

        # Collect all issues
        issues = []
        issues.extend(db_health.get("issues", []))
        issues.extend(fts_health.get("issues", []))
        issues.extend(disk_health.get("issues", []))
        issues.extend(memory_health.get("issues", []))
        issues.extend(backup_health.get("issues", []))
        issues.extend(performance_health.get("issues", []))

        check_duration = time.time() - start_time

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "check_duration_ms": round(check_duration * 1000, 2),
            "subsystems": {
                "database": db_health,
                "fts_search": fts_health,
                "disk": disk_health,
                "memory": memory_health,
                "backups": backup_health,
                "performance": performance_health
            },
            "issues": issues,
            "healthy": overall_status == HealthStatus.HEALTHY
        }

    def _check_database_health(self, db_session: Optional[Session] = None) -> Dict[str, Any]:
        """Check database connectivity and integrity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check database is readable
            cursor.execute("SELECT COUNT(*) FROM glossary_entries")
            entry_count = cursor.fetchone()[0]

            # Check for table integrity
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]

            # Check database size
            db_size_bytes = self.db_path.stat().st_size
            db_size_mb = db_size_bytes / (1024 * 1024)

            # Check for active connections (if using session)
            active_connections = 1  # At least this connection

            conn.close()

            issues = []
            if integrity != "ok":
                issues.append(f"Database integrity check failed: {integrity}")

            status = HealthStatus.HEALTHY if not issues else HealthStatus.UNHEALTHY

            return {
                "status": status,
                "entry_count": entry_count,
                "database_size_mb": round(db_size_mb, 2),
                "integrity": integrity,
                "active_connections": active_connections,
                "database_path": str(self.db_path),
                "issues": issues
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "issues": [f"Database connection failed: {str(e)}"]
            }

    def _check_fts_health(self) -> Dict[str, Any]:
        """Check FTS5 search index status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check FTS5 table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='glossary_entries_fts'
            """)
            fts_exists = cursor.fetchone() is not None

            if not fts_exists:
                conn.close()
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "fts_enabled": False,
                    "issues": ["FTS5 index not found"]
                }

            # Check FTS5 entry count
            cursor.execute("SELECT COUNT(*) FROM glossary_entries_fts")
            fts_count = cursor.fetchone()[0]

            # Check main table count
            cursor.execute("SELECT COUNT(*) FROM glossary_entries")
            main_count = cursor.fetchone()[0]

            # Check for sync issues
            count_mismatch = fts_count != main_count

            # Test search performance
            start_time = time.time()
            cursor.execute("""
                SELECT COUNT(*) FROM glossary_entries_fts
                WHERE glossary_entries_fts MATCH 'temperature'
                LIMIT 10
            """)
            search_time_ms = (time.time() - start_time) * 1000

            conn.close()

            issues = []
            if count_mismatch:
                issues.append(f"FTS5 count mismatch: {fts_count} vs {main_count} entries")

            if search_time_ms > 1000:  # > 1 second
                issues.append(f"FTS5 search slow: {search_time_ms:.2f}ms")

            status = HealthStatus.HEALTHY
            if count_mismatch:
                status = HealthStatus.DEGRADED
            if search_time_ms > 5000:  # > 5 seconds
                status = HealthStatus.UNHEALTHY

            return {
                "status": status,
                "fts_enabled": True,
                "indexed_entries": fts_count,
                "main_entries": main_count,
                "sync_status": "synchronized" if not count_mismatch else "out_of_sync",
                "search_performance_ms": round(search_time_ms, 2),
                "issues": issues
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "fts_enabled": False,
                "error": str(e),
                "issues": [f"FTS5 check failed: {str(e)}"]
            }

    def _check_disk_health(self) -> Dict[str, Any]:
        """Check disk space availability"""
        try:
            # Get disk usage for the data directory
            disk_usage = psutil.disk_usage(str(self.db_path.parent))

            free_gb = disk_usage.free / (1024 ** 3)
            total_gb = disk_usage.total / (1024 ** 3)
            used_percent = disk_usage.percent

            issues = []
            status = HealthStatus.HEALTHY

            if free_gb < self.critical_disk_threshold_gb:
                issues.append(f"Critical: Only {free_gb:.2f} GB free disk space")
                status = HealthStatus.UNHEALTHY
            elif free_gb < self.warning_disk_threshold_gb:
                issues.append(f"Warning: Low disk space - {free_gb:.2f} GB free")
                status = HealthStatus.DEGRADED

            return {
                "status": status,
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 2),
                "path": str(self.db_path.parent),
                "issues": issues
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "issues": [f"Disk check failed: {str(e)}"]
            }

    def _check_memory_health(self) -> Dict[str, Any]:
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()

            total_gb = memory.total / (1024 ** 3)
            available_gb = memory.available / (1024 ** 3)
            used_percent = memory.percent

            issues = []
            status = HealthStatus.HEALTHY

            if used_percent > self.critical_memory_threshold_percent:
                issues.append(f"Critical: Memory usage at {used_percent:.1f}%")
                status = HealthStatus.UNHEALTHY
            elif used_percent > self.warning_memory_threshold_percent:
                issues.append(f"Warning: High memory usage - {used_percent:.1f}%")
                status = HealthStatus.DEGRADED

            return {
                "status": status,
                "total_gb": round(total_gb, 2),
                "available_gb": round(available_gb, 2),
                "used_percent": round(used_percent, 2),
                "issues": issues
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "issues": [f"Memory check failed: {str(e)}"]
            }

    def _check_backup_health(self) -> Dict[str, Any]:
        """Check backup status and recency"""
        try:
            if not self.backup_dir.exists():
                return {
                    "status": HealthStatus.DEGRADED,
                    "backup_enabled": False,
                    "issues": ["Backup directory not found"]
                }

            # Find most recent backup
            backups = sorted(
                self.backup_dir.glob("glossary_backup_*.db*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Filter out .json metadata files
            backups = [b for b in backups if b.suffix != '.json']

            if not backups:
                return {
                    "status": HealthStatus.DEGRADED,
                    "backup_enabled": True,
                    "backup_count": 0,
                    "issues": ["No backups found"]
                }

            latest_backup = backups[0]
            backup_age_hours = (time.time() - latest_backup.stat().st_mtime) / 3600
            backup_size_mb = latest_backup.stat().st_size / (1024 * 1024)

            issues = []
            status = HealthStatus.HEALTHY

            # Check backup age (warn if > 24 hours, critical if > 7 days)
            if backup_age_hours > 168:  # 7 days
                issues.append(f"Critical: Last backup is {backup_age_hours / 24:.1f} days old")
                status = HealthStatus.UNHEALTHY
            elif backup_age_hours > 24:
                issues.append(f"Warning: Last backup is {backup_age_hours:.1f} hours old")
                status = HealthStatus.DEGRADED

            return {
                "status": status,
                "backup_enabled": True,
                "backup_count": len(backups),
                "latest_backup": latest_backup.name,
                "backup_age_hours": round(backup_age_hours, 2),
                "backup_size_mb": round(backup_size_mb, 2),
                "issues": issues
            }

        except Exception as e:
            return {
                "status": HealthStatus.DEGRADED,
                "error": str(e),
                "issues": [f"Backup check failed: {str(e)}"]
            }

    def _check_performance_health(self) -> Dict[str, Any]:
        """Check API performance metrics"""
        try:
            if not self.request_times:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "No performance data available yet"
                }

            # Calculate statistics
            avg_response_time = sum(self.request_times) / len(self.request_times)
            max_response_time = max(self.request_times)
            min_response_time = min(self.request_times)

            # Get recent requests (last 100)
            recent_times = self.request_times[-100:]
            recent_avg = sum(recent_times) / len(recent_times)

            issues = []
            status = HealthStatus.HEALTHY

            # Warn if average response time > 500ms, critical if > 2000ms
            if avg_response_time > 2.0:
                issues.append(f"Critical: Average response time {avg_response_time * 1000:.0f}ms")
                status = HealthStatus.UNHEALTHY
            elif avg_response_time > 0.5:
                issues.append(f"Warning: Slow average response time {avg_response_time * 1000:.0f}ms")
                status = HealthStatus.DEGRADED

            return {
                "status": status,
                "total_requests": len(self.request_times),
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "recent_avg_response_time_ms": round(recent_avg * 1000, 2),
                "max_response_time_ms": round(max_response_time * 1000, 2),
                "min_response_time_ms": round(min_response_time * 1000, 2),
                "issues": issues
            }

        except Exception as e:
            return {
                "status": HealthStatus.HEALTHY,
                "error": str(e),
                "message": "Performance tracking unavailable"
            }

    def record_request_time(self, duration_seconds: float):
        """Record a request duration for performance tracking"""
        self.request_times.append(duration_seconds)

        # Keep only the most recent requests
        if len(self.request_times) > self.max_request_history:
            self.request_times = self.request_times[-self.max_request_history:]

    def _determine_overall_status(self, statuses: List[str]) -> str:
        """Determine overall status from subsystem statuses"""
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        if any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def get_simple_health(self) -> Dict[str, Any]:
        """Get simple health status for quick checks"""
        try:
            # Just check database connectivity
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()

            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker

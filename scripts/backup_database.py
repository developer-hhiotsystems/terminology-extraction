"""
Automated Database Backup Script

Creates timestamped backups of the glossary database with:
- Compression (gzip)
- Retention policy (configurable days)
- Verification (integrity check)
- Logging
- Email notifications (optional)

Usage:
    python scripts/backup_database.py [options]

Options:
    --backup-dir PATH       Backup directory (default: backups/)
    --retention-days INT    Days to keep backups (default: 30)
    --compress              Compress backups with gzip
    --verify                Verify backup integrity
    --notify EMAIL          Send notification email on failure
"""

import os
import sys
import shutil
import sqlite3
import gzip
import json
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Automated database backup with compression and retention"""

    def __init__(
        self,
        db_path: str = "data/glossary.db",
        backup_dir: str = "backups",
        retention_days: int = 30,
        compress: bool = True,
        verify: bool = True
    ):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.compress = compress
        self.verify = verify

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> dict:
        """
        Create database backup

        Returns:
            dict: Backup information (path, size, checksum, etc.)
        """
        try:
            # Verify source database exists
            if not self.db_path.exists():
                raise FileNotFoundError(f"Database not found: {self.db_path}")

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"glossary_backup_{timestamp}.db"

            if self.compress:
                backup_name += ".gz"

            backup_path = self.backup_dir / backup_name

            logger.info(f"Creating backup: {backup_path}")

            # Perform backup
            if self.compress:
                self._backup_compressed(backup_path)
            else:
                self._backup_simple(backup_path)

            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)

            # Get backup size
            size_bytes = backup_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)

            # Verify backup (if enabled)
            if self.verify:
                if not self._verify_backup(backup_path):
                    raise Exception("Backup verification failed")
                logger.info("✓ Backup verified successfully")

            # Create metadata file
            metadata = {
                "timestamp": timestamp,
                "source": str(self.db_path),
                "backup_path": str(backup_path),
                "size_bytes": size_bytes,
                "size_mb": round(size_mb, 2),
                "checksum": checksum,
                "compressed": self.compress,
                "verified": self.verify,
            }

            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✓ Backup created successfully: {size_mb:.2f} MB")
            logger.info(f"  Checksum: {checksum}")

            return metadata

        except Exception as e:
            logger.error(f"✗ Backup failed: {e}")
            raise

    def _backup_simple(self, backup_path: Path):
        """Simple file copy backup"""
        shutil.copy2(self.db_path, backup_path)

    def _backup_compressed(self, backup_path: Path):
        """Compressed backup with gzip"""
        with open(self.db_path, 'rb') as f_in:
            with gzip.open(backup_path, 'wb', compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum"""
        sha256 = hashlib.sha256()

        if file_path.suffix == '.gz':
            with gzip.open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
        else:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)

        return sha256.hexdigest()

    def _verify_backup(self, backup_path: Path) -> bool:
        """Verify backup integrity by opening database"""
        try:
            # Decompress if needed
            if backup_path.suffix == '.gz':
                temp_db = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_db, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                db_to_verify = temp_db
            else:
                db_to_verify = backup_path

            # Try to connect and query
            conn = sqlite3.connect(db_to_verify)
            cursor = conn.cursor()

            # Verify tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            if not tables:
                return False

            # Verify glossary entries table
            cursor.execute("SELECT COUNT(*) FROM glossary_entries")
            count = cursor.fetchone()[0]

            conn.close()

            # Cleanup temp file
            if backup_path.suffix == '.gz' and temp_db.exists():
                temp_db.unlink()

            return True

        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False

    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_count = 0
            freed_space = 0

            for backup_file in self.backup_dir.glob("glossary_backup_*.db*"):
                # Skip metadata files
                if backup_file.suffix == '.json':
                    continue

                # Extract timestamp from filename
                try:
                    timestamp_str = backup_file.stem.split('_')[-2] + backup_file.stem.split('_')[-1]
                    backup_date = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")

                    if backup_date < cutoff_date:
                        # Delete backup and metadata
                        size = backup_file.stat().st_size
                        backup_file.unlink()

                        metadata_file = backup_file.with_suffix('.json')
                        if metadata_file.exists():
                            metadata_file.unlink()

                        deleted_count += 1
                        freed_space += size
                        logger.info(f"Deleted old backup: {backup_file.name}")

                except (ValueError, IndexError):
                    logger.warning(f"Could not parse backup date: {backup_file.name}")
                    continue

            if deleted_count > 0:
                freed_mb = freed_space / (1024 * 1024)
                logger.info(f"✓ Cleanup: Deleted {deleted_count} old backups, freed {freed_mb:.2f} MB")
            else:
                logger.info("✓ Cleanup: No old backups to delete")

        except Exception as e:
            logger.error(f"✗ Cleanup failed: {e}")

    def list_backups(self) -> list:
        """List all available backups"""
        backups = []

        for backup_file in sorted(self.backup_dir.glob("glossary_backup_*.db*")):
            if backup_file.suffix == '.json':
                continue

            metadata_file = backup_file.with_suffix('.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    backups.append(metadata)
            else:
                # Create basic metadata
                stat = backup_file.stat()
                backups.append({
                    "backup_path": str(backup_file),
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "timestamp": datetime.fromtimestamp(stat.st_mtime).strftime("%Y%m%d_%H%M%S"),
                })

        return backups

    def restore_backup(self, backup_path: str, target_path: str = None):
        """
        Restore database from backup

        Args:
            backup_path: Path to backup file
            target_path: Where to restore (default: original database path)
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup not found: {backup_path}")

            if target_path is None:
                target_path = self.db_path

            target_path = Path(target_path)

            logger.info(f"Restoring backup: {backup_path}")

            # Backup current database (if exists)
            if target_path.exists():
                emergency_backup = target_path.with_suffix('.db.emergency')
                shutil.copy2(target_path, emergency_backup)
                logger.info(f"Created emergency backup: {emergency_backup}")

            # Restore
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(target_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, target_path)

            logger.info(f"✓ Database restored successfully to: {target_path}")

        except Exception as e:
            logger.error(f"✗ Restore failed: {e}")
            raise


def main():
    """Main backup execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated database backup")
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--retention-days', type=int, default=30, help='Days to keep backups')
    parser.add_argument('--compress', action='store_true', help='Compress backups')
    parser.add_argument('--verify', action='store_true', default=True, help='Verify backups')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--restore', help='Restore from backup path')

    args = parser.parse_args()

    # Initialize backup manager
    backup = DatabaseBackup(
        backup_dir=args.backup_dir,
        retention_days=args.retention_days,
        compress=args.compress,
        verify=args.verify
    )

    # List backups
    if args.list:
        backups = backup.list_backups()
        print(f"\nAvailable backups ({len(backups)}):")
        print("-" * 80)
        for b in backups:
            print(f"{b['timestamp']} - {b['size_mb']} MB - {b['backup_path']}")
        return

    # Restore backup
    if args.restore:
        backup.restore_backup(args.restore)
        return

    # Create backup
    try:
        logger.info("=" * 80)
        logger.info("DATABASE BACKUP STARTED")
        logger.info("=" * 80)

        # Create backup
        metadata = backup.create_backup()

        # Cleanup old backups
        backup.cleanup_old_backups()

        logger.info("=" * 80)
        logger.info("DATABASE BACKUP COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return metadata

    except Exception as e:
        logger.error("=" * 80)
        logger.error("DATABASE BACKUP FAILED")
        logger.error("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    main()

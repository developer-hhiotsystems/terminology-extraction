#!/usr/bin/env python
"""SQLite database backup script with retention policy"""
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def backup_database(db_path: Path, backup_dir: Path) -> Path:
    """Create a backup of the SQLite database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"glossary_backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename

    # Ensure backup directory exists
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Check if database exists
    if not db_path.exists():
        print(f"[WARN] Database does not exist yet: {db_path}")
        print("This is normal if you haven't created any data yet.")
        return None

    # Perform backup using SQLite's backup API (safer than file copy)
    try:
        # Connect to source database
        source_conn = sqlite3.connect(db_path)

        # Connect to backup database
        backup_conn = sqlite3.connect(backup_path)

        # Perform backup
        with backup_conn:
            source_conn.backup(backup_conn)

        source_conn.close()
        backup_conn.close()

        backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Backup created: {backup_filename} ({backup_size_mb:.2f} MB)")

        return backup_path

    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        if backup_path.exists():
            backup_path.unlink()
        return None

def cleanup_old_backups(backup_dir: Path, retention_days: int = 30):
    """Remove backups older than retention period"""
    if not backup_dir.exists():
        return

    cutoff_date = datetime.now() - timedelta(days=retention_days)
    removed_count = 0

    for backup_file in backup_dir.glob("glossary_backup_*.db"):
        file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

        if file_mtime < cutoff_date:
            try:
                backup_file.unlink()
                removed_count += 1
                print(f"[INFO] Removed old backup: {backup_file.name}")
            except Exception as e:
                print(f"[WARN] Could not remove {backup_file.name}: {e}")

    if removed_count > 0:
        print(f"[OK] Removed {removed_count} old backup(s)")

def list_backups(backup_dir: Path):
    """List all available backups"""
    if not backup_dir.exists():
        print("[INFO] No backups directory found")
        return

    backups = sorted(backup_dir.glob("glossary_backup_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not backups:
        print("[INFO] No backups found")
        return

    print(f"\nAvailable Backups ({len(backups)}):")
    print("-" * 70)

    for backup in backups:
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        age = datetime.now() - mtime

        if age.days > 0:
            age_str = f"{age.days} day(s) ago"
        elif age.seconds > 3600:
            age_str = f"{age.seconds // 3600} hour(s) ago"
        else:
            age_str = f"{age.seconds // 60} minute(s) ago"

        print(f"  {backup.name}")
        print(f"    Size: {size_mb:.2f} MB | Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')} ({age_str})")

def restore_backup(backup_path: Path, db_path: Path):
    """Restore database from backup"""
    if not backup_path.exists():
        print(f"[ERROR] Backup file not found: {backup_path}")
        return False

    # Create a backup of current database before restoring
    if db_path.exists():
        current_backup = db_path.parent / f"{db_path.stem}_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, current_backup)
        print(f"[INFO] Current database backed up to: {current_backup.name}")

    try:
        shutil.copy2(backup_path, db_path)
        print(f"[OK] Database restored from: {backup_path.name}")
        return True
    except Exception as e:
        print(f"[ERROR] Restore failed: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  SQLite Database Backup Utility")
    print("="*70 + "\n")

    # Configuration
    db_path = Path("data/glossary.db")
    backup_dir = Path("backups/sqlite")
    retention_days = 30

    print("Configuration:")
    print(f"  Database: {db_path}")
    print(f"  Backup Directory: {backup_dir}")
    print(f"  Retention Policy: {retention_days} days")
    print("")

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        print("Commands:")
        print("  backup  - Create a new backup")
        print("  list    - List all backups")
        print("  restore - Restore from a backup")
        print("  cleanup - Remove old backups")
        print("")
        command = input("Enter command (backup/list/restore/cleanup): ").lower()

    if command == "backup":
        print("\nCreating backup...")
        backup_path = backup_database(db_path, backup_dir)
        if backup_path:
            print("\n[OK] Backup completed successfully!")

    elif command == "list":
        list_backups(backup_dir)
        print("")

    elif command == "restore":
        list_backups(backup_dir)
        print("")

        backup_filename = input("Enter backup filename to restore (or 'cancel'): ").strip()
        if backup_filename.lower() == 'cancel':
            print("\nRestore cancelled.\n")
            return

        backup_path = backup_dir / backup_filename

        confirm = input(f"\n[WARN] This will replace the current database. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            restore_backup(backup_path, db_path)
        else:
            print("\nRestore cancelled.\n")

    elif command == "cleanup":
        print(f"\nRemoving backups older than {retention_days} days...")
        cleanup_old_backups(backup_dir, retention_days)
        print("\n[OK] Cleanup completed\n")

    else:
        print(f"\n[ERROR] Unknown command: {command}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()

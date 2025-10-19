#!/bin/bash
# Automated Database Backup Script for Linux/Mac
# Runs the Python backup script with default settings

set -e  # Exit on error

echo "================================================================================"
echo "Glossary Database Backup - Linux/Mac"
echo "================================================================================"
echo ""

# Change to project directory
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Run backup script with compression and verification
python scripts/backup_database.py --compress --verify

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Backup failed!"
    echo "Check logs/backup.log for details"
    exit 1
fi

echo ""
echo "Backup completed successfully!"
echo ""

# List recent backups
python scripts/backup_database.py --list

echo ""
echo "================================================================================"

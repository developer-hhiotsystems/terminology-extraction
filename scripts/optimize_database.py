"""
Database Optimization Script

Performs database optimization tasks:
- Create/rebuild indexes
- Analyze tables for query optimization
- Vacuum database to reclaim space
- Check database integrity
- Generate optimization report

Usage:
    python scripts/optimize_database.py [options]

Options:
    --analyze          Update query planner statistics
    --vacuum           Reclaim space and defragment
    --reindex          Rebuild all indexes
    --integrity        Check database integrity
    --create-indexes   Create recommended indexes
    --all              Run all optimizations
    --dry-run          Show what would be done without executing
"""

import sqlite3
import argparse
import time
from pathlib import Path
from datetime import datetime
import sys


class DatabaseOptimizer:
    """Database optimization utility"""

    def __init__(self, db_path: str = "data/glossary.db"):
        """
        Initialize database optimizer

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def analyze_tables(self) -> dict:
        """
        Run ANALYZE to update query planner statistics

        Returns:
            dict: Analysis results
        """
        print("Running ANALYZE...")
        start_time = time.time()

        # Get list of tables
        self.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [row[0] for row in self.cursor.fetchall()]

        # Analyze each table
        for table in tables:
            print(f"  Analyzing table: {table}")
            self.cursor.execute(f"ANALYZE {table}")

        # Global analyze
        self.cursor.execute("ANALYZE")
        self.conn.commit()

        duration = time.time() - start_time

        return {
            "operation": "ANALYZE",
            "tables_analyzed": len(tables),
            "duration_seconds": round(duration, 2),
            "status": "success"
        }

    def vacuum_database(self) -> dict:
        """
        Run VACUUM to reclaim space and defragment

        Returns:
            dict: Vacuum results
        """
        print("Running VACUUM...")
        start_time = time.time()

        # Get size before
        size_before = self.db_path.stat().st_size

        # Vacuum
        self.cursor.execute("VACUUM")

        # Get size after
        size_after = self.db_path.stat().st_size
        space_saved = size_before - size_after

        duration = time.time() - start_time

        return {
            "operation": "VACUUM",
            "size_before_mb": round(size_before / 1024 / 1024, 2),
            "size_after_mb": round(size_after / 1024 / 1024, 2),
            "space_saved_mb": round(space_saved / 1024 / 1024, 2),
            "duration_seconds": round(duration, 2),
            "status": "success"
        }

    def reindex_database(self) -> dict:
        """
        Rebuild all indexes

        Returns:
            dict: Reindex results
        """
        print("Running REINDEX...")
        start_time = time.time()

        # Get list of indexes
        self.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        indexes = [row[0] for row in self.cursor.fetchall()]

        # Reindex each
        for index in indexes:
            print(f"  Reindexing: {index}")
            self.cursor.execute(f"REINDEX {index}")

        # Global reindex
        self.cursor.execute("REINDEX")
        self.conn.commit()

        duration = time.time() - start_time

        return {
            "operation": "REINDEX",
            "indexes_rebuilt": len(indexes),
            "duration_seconds": round(duration, 2),
            "status": "success"
        }

    def check_integrity(self) -> dict:
        """
        Check database integrity

        Returns:
            dict: Integrity check results
        """
        print("Checking database integrity...")
        start_time = time.time()

        self.cursor.execute("PRAGMA integrity_check")
        result = self.cursor.fetchone()[0]

        duration = time.time() - start_time

        is_ok = result == "ok"

        return {
            "operation": "INTEGRITY_CHECK",
            "result": result,
            "status": "success" if is_ok else "failed",
            "duration_seconds": round(duration, 2)
        }

    def create_indexes(self) -> dict:
        """
        Create recommended indexes

        Returns:
            dict: Index creation results
        """
        print("Creating recommended indexes...")
        start_time = time.time()

        # Read SQL file
        sql_file = Path("src/backend/optimization/database_indexes.sql")

        if not sql_file.exists():
            return {
                "operation": "CREATE_INDEXES",
                "status": "skipped",
                "message": "Index SQL file not found"
            }

        with open(sql_file, 'r') as f:
            sql_script = f.read()

        # Execute SQL script
        self.cursor.executescript(sql_script)
        self.conn.commit()

        duration = time.time() - start_time

        # Count created indexes
        self.cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        index_count = self.cursor.fetchone()[0]

        return {
            "operation": "CREATE_INDEXES",
            "total_indexes": index_count,
            "duration_seconds": round(duration, 2),
            "status": "success"
        }

    def get_database_stats(self) -> dict:
        """
        Get database statistics

        Returns:
            dict: Database statistics
        """
        stats = {}

        # Database size
        stats["database_size_mb"] = round(self.db_path.stat().st_size / 1024 / 1024, 2)

        # Table counts
        self.cursor.execute("SELECT COUNT(*) FROM glossary_entries")
        stats["glossary_entries"] = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM glossary_entries_fts")
        stats["fts_entries"] = self.cursor.fetchone()[0]

        try:
            self.cursor.execute("SELECT COUNT(*) FROM term_relationships")
            stats["relationships"] = self.cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats["relationships"] = 0

        # Index count
        self.cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        stats["indexes"] = self.cursor.fetchone()[0]

        # Page count
        self.cursor.execute("PRAGMA page_count")
        stats["page_count"] = self.cursor.fetchone()[0]

        # Page size
        self.cursor.execute("PRAGMA page_size")
        stats["page_size"] = self.cursor.fetchone()[0]

        # Freelist count (unused pages)
        self.cursor.execute("PRAGMA freelist_count")
        stats["freelist_count"] = self.cursor.fetchone()[0]

        return stats

    def generate_report(self, results: list) -> str:
        """
        Generate optimization report

        Args:
            results: List of operation results

        Returns:
            str: Formatted report
        """
        report = []
        report.append("=" * 80)
        report.append("DATABASE OPTIMIZATION REPORT")
        report.append("=" * 80)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Database: {self.db_path}")
        report.append("")

        # Database stats
        stats = self.get_database_stats()
        report.append("Database Statistics:")
        report.append("-" * 80)
        for key, value in stats.items():
            report.append(f"  {key}: {value}")
        report.append("")

        # Operations
        report.append("Operations Performed:")
        report.append("-" * 80)

        total_duration = 0
        for result in results:
            operation = result.get("operation", "UNKNOWN")
            status = result.get("status", "unknown")
            duration = result.get("duration_seconds", 0)
            total_duration += duration

            report.append(f"\n{operation}:")
            for key, value in result.items():
                if key not in ["operation"]:
                    report.append(f"  {key}: {value}")

        report.append("")
        report.append("=" * 80)
        report.append(f"Total Duration: {round(total_duration, 2)} seconds")
        report.append("=" * 80)

        return "\n".join(report)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main optimization execution"""
    parser = argparse.ArgumentParser(description="Database optimization utility")
    parser.add_argument('--analyze', action='store_true', help='Update query planner statistics')
    parser.add_argument('--vacuum', action='store_true', help='Reclaim space and defragment')
    parser.add_argument('--reindex', action='store_true', help='Rebuild all indexes')
    parser.add_argument('--integrity', action='store_true', help='Check database integrity')
    parser.add_argument('--create-indexes', action='store_true', help='Create recommended indexes')
    parser.add_argument('--all', action='store_true', help='Run all optimizations')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--db-path', default='data/glossary.db', help='Database path')

    args = parser.parse_args()

    # If --all specified, enable all operations
    if args.all:
        args.create_indexes = True
        args.analyze = True
        args.integrity = True
        args.reindex = True
        args.vacuum = True

    # If no operations specified, show help
    if not any([args.analyze, args.vacuum, args.reindex, args.integrity, args.create_indexes]):
        parser.print_help()
        sys.exit(0)

    print("=" * 80)
    print("DATABASE OPTIMIZATION")
    print("=" * 80)
    print(f"Database: {args.db_path}")

    if args.dry_run:
        print("\nDRY RUN MODE - No changes will be made")
        print("\nOperations that would be performed:")
        if args.create_indexes:
            print("  - Create recommended indexes")
        if args.analyze:
            print("  - Analyze tables")
        if args.integrity:
            print("  - Check database integrity")
        if args.reindex:
            print("  - Rebuild indexes")
        if args.vacuum:
            print("  - Vacuum database")
        print("")
        sys.exit(0)

    try:
        optimizer = DatabaseOptimizer(db_path=args.db_path)
        results = []

        # Execute operations in recommended order
        if args.create_indexes:
            results.append(optimizer.create_indexes())

        if args.integrity:
            result = optimizer.check_integrity()
            results.append(result)
            if result["status"] != "success":
                print("\n⚠️  WARNING: Database integrity check failed!")
                print(f"Result: {result['result']}")
                print("\nRecommendation: Restore from backup before continuing")
                sys.exit(1)

        if args.analyze:
            results.append(optimizer.analyze_tables())

        if args.reindex:
            results.append(optimizer.reindex_database())

        if args.vacuum:
            results.append(optimizer.vacuum_database())

        # Generate report
        report = optimizer.generate_report(results)
        print("\n" + report)

        # Save report
        report_path = Path("logs") / f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\nReport saved to: {report_path}")

        optimizer.close()

        print("\n✓ Optimization completed successfully!")

    except Exception as e:
        print(f"\n✗ Optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

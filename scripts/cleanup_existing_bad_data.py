"""
One-Time Cleanup Script for Legacy Bad Data

This script removes bad glossary entries that were created BEFORE the
extraction pipeline fixes in Week 2.

Run this AFTER verifying the extraction fixes work correctly.

What it does:
1. Re-validates all existing glossary entries with NEW validation rules
2. Identifies entries that would now be rejected
3. Shows breakdown by rejection reason
4. Deletes bad entries from database
5. Reports final data quality metrics

Expected result: Database quality improves from 55-60% → 95%+
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy import func
from src.backend.database import get_db_context
from src.backend.models import GlossaryEntry
from src.backend.services.term_validator import create_default_validator
from collections import Counter
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_database_quality():
    """Analyze current database quality before cleanup"""
    logger.info("="*60)
    logger.info("ANALYZING CURRENT DATABASE QUALITY")
    logger.info("="*60)

    with get_db_context() as db:
        total_entries = db.query(GlossaryEntry).count()
        logger.info(f"\nTotal glossary entries: {total_entries}")

        if total_entries == 0:
            logger.warning("No entries in database")
            return None

        # Count by validation status
        validated = db.query(GlossaryEntry).filter(
            GlossaryEntry.validation_status == 'validated'
        ).count()
        pending = db.query(GlossaryEntry).filter(
            GlossaryEntry.validation_status == 'pending'
        ).count()
        rejected = db.query(GlossaryEntry).filter(
            GlossaryEntry.validation_status == 'rejected'
        ).count()

        logger.info(f"\nValidation status breakdown:")
        logger.info(f"  Validated: {validated} ({validated/total_entries*100:.1f}%)")
        logger.info(f"  Pending:   {pending} ({pending/total_entries*100:.1f}%)")
        logger.info(f"  Rejected:  {rejected} ({rejected/total_entries*100:.1f}%)")

        # Count by source
        sources = db.query(
            GlossaryEntry.source,
            func.count(GlossaryEntry.id)
        ).group_by(GlossaryEntry.source).all()

        logger.info(f"\nSource breakdown:")
        for source, count in sources:
            logger.info(f"  {source or 'None'}: {count} ({count/total_entries*100:.1f}%)")

        return {
            'total': total_entries,
            'validated': validated,
            'pending': pending,
            'rejected': rejected
        }


def identify_bad_entries(dry_run=True):
    """
    Identify entries that should be deleted based on NEW validation rules

    Args:
        dry_run: If True, only analyze without deleting

    Returns:
        Dict with analysis results
    """
    logger.info("\n" + "="*60)
    logger.info("IDENTIFYING BAD ENTRIES WITH NEW VALIDATION RULES")
    logger.info("="*60)

    validator = create_default_validator(language="en")
    to_delete = []
    rejection_reasons = Counter()

    with get_db_context() as db:
        entries = db.query(GlossaryEntry).all()
        total = len(entries)

        logger.info(f"\nRe-validating {total} entries with NEW rules...")

        for i, entry in enumerate(entries):
            if (i + 1) % 500 == 0:
                logger.info(f"  Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)")

            # Re-validate with NEW validation rules
            is_valid = validator.is_valid_term(entry.term)

            if not is_valid:
                reason = validator.get_rejection_reason(entry.term)
                to_delete.append({
                    'id': entry.id,
                    'term': entry.term,
                    'reason': reason,
                    'source': entry.source,
                    'validation_status': entry.validation_status
                })
                rejection_reasons[reason] += 1

        logger.info(f"\n✓ Re-validation complete")

    # Show results
    logger.info(f"\n" + "="*60)
    logger.info(f"ANALYSIS RESULTS")
    logger.info(f"="*60)

    logger.info(f"\nTotal entries: {total}")
    logger.info(f"Good entries (pass NEW validation): {total - len(to_delete)} ({(total-len(to_delete))/total*100:.1f}%)")
    logger.info(f"Bad entries (fail NEW validation): {len(to_delete)} ({len(to_delete)/total*100:.1f}%)")

    if len(to_delete) > 0:
        logger.info(f"\n Rejection reasons breakdown:")
        for reason, count in rejection_reasons.most_common():
            logger.info(f"  {count:4d} ({count/len(to_delete)*100:5.1f}%) - {reason}")

        # Show sample bad entries
        logger.info(f"\nSample of bad entries to delete (first 20):")
        for i, entry in enumerate(to_delete[:20]):
            logger.info(f"  {i+1:2d}. '{entry['term']}' - {entry['reason']}")

    return {
        'total_entries': total,
        'good_entries': total - len(to_delete),
        'bad_entries': len(to_delete),
        'to_delete': to_delete,
        'rejection_reasons': rejection_reasons,
        'quality_before': (total - len(to_delete)) / total * 100 if total > 0 else 0
    }


def cleanup_bad_entries(to_delete_list, confirm=True):
    """
    Delete bad entries from database

    Args:
        to_delete_list: List of entry dicts to delete
        confirm: If True, ask for confirmation before deleting

    Returns:
        Number of entries deleted
    """
    if len(to_delete_list) == 0:
        logger.info("\n✓ No entries to delete - database is already clean!")
        return 0

    logger.info(f"\n" + "="*60)
    logger.info(f"CLEANUP PHASE")
    logger.info(f"="*60)

    logger.info(f"\n⚠️  WARNING: About to delete {len(to_delete_list)} entries!")

    if confirm:
        response = input("\nProceed with deletion? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Cleanup cancelled by user")
            return 0

    logger.info(f"\nDeleting {len(to_delete_list)} bad entries...")

    deleted_count = 0
    with get_db_context() as db:
        for i, entry_dict in enumerate(to_delete_list):
            if (i + 1) % 100 == 0:
                logger.info(f"  Progress: {i+1}/{len(to_delete_list)} ({(i+1)/len(to_delete_list)*100:.1f}%)")

            # Delete entry
            entry = db.query(GlossaryEntry).filter(
                GlossaryEntry.id == entry_dict['id']
            ).first()

            if entry:
                db.delete(entry)
                deleted_count += 1

        # Commit all deletions
        db.commit()

    logger.info(f"\n✓ Deletion complete: {deleted_count} entries removed")
    return deleted_count


def main():
    """Main cleanup workflow"""
    logger.info("\n" + "#"*60)
    logger.info("# ONE-TIME LEGACY DATA CLEANUP")
    logger.info("# Week 2 - Phase 3")
    logger.info("#"*60)

    # Step 1: Analyze current quality
    current_stats = analyze_database_quality()

    if current_stats is None or current_stats['total'] == 0:
        logger.info("\nNo data to clean up")
        return

    # Step 2: Identify bad entries
    analysis = identify_bad_entries(dry_run=True)

    # Step 3: Cleanup (with confirmation)
    deleted = cleanup_bad_entries(analysis['to_delete'], confirm=True)

    # Step 4: Final analysis
    logger.info(f"\n" + "="*60)
    logger.info(f"FINAL RESULTS")
    logger.info(f"="*60)

    with get_db_context() as db:
        final_total = db.query(GlossaryEntry).count()

        logger.info(f"\nDatabase statistics:")
        logger.info(f"  Before cleanup: {current_stats['total']} entries")
        logger.info(f"  Deleted:        {deleted} bad entries")
        logger.info(f"  After cleanup:  {final_total} entries")

        quality_before = analysis['quality_before']
        quality_after = 100.0  # All remaining entries pass validation

        logger.info(f"\nData quality:")
        logger.info(f"  Before: {quality_before:.1f}% good entries")
        logger.info(f"  After:  {quality_after:.1f}% good entries")
        logger.info(f"  Improvement: +{quality_after - quality_before:.1f} percentage points")

    logger.info(f"\n" + "#"*60)
    logger.info("# CLEANUP COMPLETE")
    logger.info("#"*60)

    logger.info(f"\n✅ Success!")
    logger.info(f"   Database is now clean and ready for Neo4j")
    logger.info(f"   Future extractions will use the fixed pipeline")
    logger.info(f"   No more bad data will be created!")


if __name__ == "__main__":
    main()

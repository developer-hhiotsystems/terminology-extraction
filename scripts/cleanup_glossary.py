"""
Database Cleanup Script - Remove Low-Quality Glossary Entries

This script identifies and removes low-quality glossary entries based on
validation criteria from TermValidator.

Usage:
    # Dry run (show what would be deleted)
    python scripts/cleanup_glossary.py --dry-run

    # Actually delete bad entries
    python scripts/cleanup_glossary.py --confirm

    # Only flag as rejected (don't delete)
    python scripts/cleanup_glossary.py --flag-only
"""
import argparse
from src.backend.database import SessionLocal
from src.backend.models import GlossaryEntry
from src.backend.services.term_validator import create_default_validator
import json

def analyze_database(db, validator):
    """
    Analyze current glossary entries for quality issues

    Returns:
        dict with analysis results
    """
    entries = db.query(GlossaryEntry).all()

    analysis = {
        'total_entries': len(entries),
        'invalid_entries': [],
        'valid_entries': [],
        'issues_breakdown': {
            'too_short': 0,
            'numeric_only': 0,
            'stopword': 0,
            'symbol_heavy': 0,
            'fragment': 0,
            'invalid_chars': 0,
            'other': 0
        }
    }

    for entry in entries:
        term = entry.term

        if validator.is_valid_term(term):
            analysis['valid_entries'].append(entry.id)
        else:
            reason = validator.get_rejection_reason(term)
            analysis['invalid_entries'].append({
                'id': entry.id,
                'term': term,
                'reason': reason,
                'frequency': len(entry.term_documents) if hasattr(entry, 'term_documents') else 0,
                'validation_status': entry.validation_status
            })

            # Categorize the issue
            if 'too short' in reason.lower():
                analysis['issues_breakdown']['too_short'] += 1
            elif 'numeric' in reason.lower() or 'number' in reason.lower():
                analysis['issues_breakdown']['numeric_only'] += 1
            elif 'stopword' in reason.lower() or 'stop word' in reason.lower():
                analysis['issues_breakdown']['stopword'] += 1
            elif 'symbol' in reason.lower():
                analysis['issues_breakdown']['symbol_heavy'] += 1
            elif 'fragment' in reason.lower() or 'incomplete' in reason.lower():
                analysis['issues_breakdown']['fragment'] += 1
            elif 'character' in reason.lower():
                analysis['issues_breakdown']['invalid_chars'] += 1
            else:
                analysis['issues_breakdown']['other'] += 1

    analysis['invalid_count'] = len(analysis['invalid_entries'])
    analysis['valid_count'] = len(analysis['valid_entries'])
    analysis['invalid_percentage'] = (analysis['invalid_count'] / analysis['total_entries'] * 100) if analysis['total_entries'] > 0 else 0

    return analysis

def print_analysis(analysis):
    """Print analysis results in a readable format"""
    print("=" * 70)
    print("GLOSSARY QUALITY ANALYSIS")
    print("=" * 70)
    print(f"\nTotal entries: {analysis['total_entries']}")
    print(f"  ✅ Valid: {analysis['valid_count']} ({100 - analysis['invalid_percentage']:.1f}%)")
    print(f"  ❌ Invalid: {analysis['invalid_count']} ({analysis['invalid_percentage']:.1f}%)")

    print("\n" + "-" * 70)
    print("ISSUES BREAKDOWN:")
    print("-" * 70)
    for issue_type, count in analysis['issues_breakdown'].items():
        if count > 0:
            print(f"  {issue_type.replace('_', ' ').title()}: {count}")

    print("\n" + "-" * 70)
    print("SAMPLE INVALID ENTRIES (First 30):")
    print("-" * 70)
    for i, entry in enumerate(analysis['invalid_entries'][:30], 1):
        status_icon = "⏸" if entry['validation_status'] == 'pending' else "✓" if entry['validation_status'] == 'validated' else "✗"
        print(f"{i:2}. {status_icon} '{entry['term']}' - {entry['reason']}")

    if len(analysis['invalid_entries']) > 30:
        print(f"\n... and {len(analysis['invalid_entries']) - 30} more invalid entries")

def flag_invalid_entries(db, analysis):
    """Mark invalid entries as rejected without deleting them"""
    print(f"\n🏴 Flagging {len(analysis['invalid_entries'])} entries as 'rejected'...")

    updated = 0
    for entry_data in analysis['invalid_entries']:
        entry = db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_data['id']).first()
        if entry and entry.validation_status != 'rejected':
            entry.validation_status = 'rejected'
            updated += 1

    db.commit()
    print(f"✅ Flagged {updated} entries as rejected")

def delete_invalid_entries(db, analysis):
    """Actually delete invalid entries from the database"""
    print(f"\n🗑️ Deleting {len(analysis['invalid_entries'])} invalid entries...")

    deleted = 0
    for entry_data in analysis['invalid_entries']:
        entry = db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_data['id']).first()
        if entry:
            db.delete(entry)
            deleted += 1

    db.commit()
    print(f"✅ Deleted {deleted} entries from database")

def save_report(analysis, filename='glossary_cleanup_report.json'):
    """Save detailed analysis report to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Detailed report saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Clean up low-quality glossary entries')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without making changes')
    parser.add_argument('--confirm', action='store_true',
                       help='Actually delete invalid entries (DESTRUCTIVE)')
    parser.add_argument('--flag-only', action='store_true',
                       help='Flag entries as rejected instead of deleting')
    parser.add_argument('--language', default='en', choices=['en', 'de'],
                       help='Language for validation (default: en)')
    parser.add_argument('--profile', default='default',
                       choices=['strict', 'default', 'lenient', 'technical'],
                       help='Validation profile to use (default: default)')

    args = parser.parse_args()

    # Create database session
    db = SessionLocal()

    try:
        # Create validator with specified profile
        print(f"Using validation profile: {args.profile}")
        print(f"Language: {args.language}")

        if args.profile == 'strict':
            from config.validation_config import get_validation_profile
            config = get_validation_profile('strict', args.language)
            from src.backend.services.term_validator import TermValidator
            validator = TermValidator(config)
        elif args.profile == 'lenient':
            from config.validation_config import get_validation_profile
            config = get_validation_profile('lenient', args.language)
            from src.backend.services.term_validator import TermValidator
            validator = TermValidator(config)
        elif args.profile == 'technical':
            from config.validation_config import get_validation_profile
            config = get_validation_profile('technical', args.language)
            from src.backend.services.term_validator import TermValidator
            validator = TermValidator(config)
        else:
            validator = create_default_validator(args.language)

        # Analyze database
        print("\n🔍 Analyzing glossary database...\n")
        analysis = analyze_database(db, validator)

        # Print analysis
        print_analysis(analysis)

        # Save report
        save_report(analysis)

        # Take action based on arguments
        if args.dry_run:
            print("\n" + "=" * 70)
            print("DRY RUN MODE - No changes made to database")
            print("=" * 70)
            print(f"\nWould delete {len(analysis['invalid_entries'])} entries")
            print("\nRe-run with --confirm to actually delete these entries")
            print("Or use --flag-only to mark them as rejected without deleting")

        elif args.flag_only:
            print("\n" + "=" * 70)
            print("FLAG ONLY MODE")
            print("=" * 70)
            flag_invalid_entries(db, analysis)

        elif args.confirm:
            print("\n" + "=" * 70)
            print("⚠️  DESTRUCTIVE MODE - DELETING ENTRIES")
            print("=" * 70)

            # Final confirmation
            response = input(f"\nAre you SURE you want to delete {len(analysis['invalid_entries'])} entries? (yes/no): ")
            if response.lower() == 'yes':
                delete_invalid_entries(db, analysis)
                print("\n✅ Database cleanup complete!")
            else:
                print("\n❌ Deletion cancelled")
        else:
            print("\n" + "=" * 70)
            print("No action taken - use --dry-run, --flag-only, or --confirm")
            print("=" * 70)

    finally:
        db.close()

if __name__ == '__main__':
    main()

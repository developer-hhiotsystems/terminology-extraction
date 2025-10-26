"""
Batch Relationship Extraction Script

Processes all existing glossary entries to extract semantic relationships
using the NLP pipeline. Useful for:
- Initial relationship extraction from existing data
- Re-processing after improving extraction algorithms
- Batch updates with new relationship types

Usage:
    python scripts/batch_extract_relationships.py [options]

Options:
    --min-confidence FLOAT   Minimum confidence threshold (0.0-1.0, default: 0.5)
    --limit INT              Process only N entries (default: all)
    --skip-existing          Skip entries that already have relationships
    --dry-run                Show what would be extracted without saving
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.base_models import GlossaryEntry
from src.backend.models.relationship import TermRelationship
from src.backend.nlp.relationship_extractor import RelationshipExtractor
from datetime import datetime


def batch_extract_relationships(
    min_confidence: float = 0.5,
    limit: int = None,
    skip_existing: bool = False,
    dry_run: bool = False
):
    """
    Extract relationships for all glossary entries

    Args:
        min_confidence: Minimum confidence threshold
        limit: Maximum number of entries to process
        skip_existing: Skip entries that already have relationships
        dry_run: Don't save to database, just show results
    """
    # Connect to database
    database_path = project_root / "data" / "glossary.db"
    engine = create_engine(f"sqlite:///{database_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Initialize NLP extractor
    print("Initializing NLP relationship extractor...")
    try:
        extractor = RelationshipExtractor()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        print("\nPlease install spaCy model:")
        print("  python -m spacy download en_core_web_sm")
        return

    # Get all glossary entries
    print("\nFetching glossary entries...")
    query = session.query(GlossaryEntry)

    if skip_existing:
        # Get IDs of entries that already have relationships
        existing_ids = session.query(TermRelationship.source_term_id).distinct().all()
        existing_ids = [id[0] for id in existing_ids]
        query = query.filter(~GlossaryEntry.id.in_(existing_ids))

    if limit:
        query = query.limit(limit)

    entries = query.all()
    total_entries = len(entries)

    print(f"Processing {total_entries} entries...")
    print(f"Minimum confidence: {min_confidence}")
    print(f"Dry run: {dry_run}")
    print()

    # Get all terms for relationship extraction
    all_entries = session.query(GlossaryEntry).all()
    all_terms = [e.term for e in all_entries]

    # Statistics
    stats = {
        "entries_processed": 0,
        "relationships_extracted": 0,
        "relationships_created": 0,
        "relationships_skipped": 0,
        "errors": 0,
    }

    # Process each entry
    for i, entry in enumerate(entries, 1):
        print(f"[{i}/{total_entries}] Processing: {entry.term}")

        try:
            # Prepare definitions
            definitions = []
            if entry.definitions:
                for def_dict in entry.definitions:
                    definitions.append({
                        "definition_text": def_dict.get("definition_text", ""),
                        "context": def_dict.get("context", "")
                    })

            if not definitions:
                print(f"  - No definitions, skipping")
                continue

            # Extract relationships
            extracted = extractor.extract_from_glossary_entry(
                entry.term,
                definitions,
                all_terms,
                min_confidence
            )

            stats["entries_processed"] += 1
            stats["relationships_extracted"] += len(extracted)

            if not extracted:
                print(f"  - No relationships found")
                continue

            print(f"  - Found {len(extracted)} relationships:")

            # Save relationships
            for rel in extracted:
                # Find target term
                target_entry = session.query(GlossaryEntry).filter(
                    GlossaryEntry.term == rel.target_term
                ).first()

                if not target_entry:
                    stats["relationships_skipped"] += 1
                    continue

                # Check for duplicate
                existing = session.query(TermRelationship).filter(
                    TermRelationship.source_term_id == entry.id,
                    TermRelationship.target_term_id == target_entry.id,
                    TermRelationship.relation_type == rel.relation_type.value
                ).first()

                if existing:
                    print(f"    - {rel.relation_type.value} → {rel.target_term} (DUPLICATE, skipped)")
                    stats["relationships_skipped"] += 1
                    continue

                # Create relationship
                print(f"    - {rel.relation_type.value} → {rel.target_term} (confidence: {rel.confidence:.2f})")

                if not dry_run:
                    db_rel = TermRelationship(
                        source_term_id=entry.id,
                        target_term_id=target_entry.id,
                        relation_type=rel.relation_type.value,
                        confidence=rel.confidence,
                        evidence=rel.evidence,
                        context=rel.context,
                        extraction_method="batch_processing"
                    )
                    session.add(db_rel)
                    stats["relationships_created"] += 1

            # Commit every 10 entries
            if not dry_run and i % 10 == 0:
                session.commit()
                print(f"  - Committed batch (total: {stats['relationships_created']} relationships)")

        except Exception as e:
            print(f"  - ERROR: {e}")
            stats["errors"] += 1
            continue

    # Final commit
    if not dry_run:
        session.commit()

    # Print summary
    print("\n" + "=" * 60)
    print("BATCH EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Entries processed:         {stats['entries_processed']}")
    print(f"Relationships extracted:   {stats['relationships_extracted']}")
    print(f"Relationships created:     {stats['relationships_created']}")
    print(f"Relationships skipped:     {stats['relationships_skipped']}")
    print(f"Errors:                    {stats['errors']}")
    print("=" * 60)

    if dry_run:
        print("\nDRY RUN - No changes were saved to the database")
    else:
        print(f"\n[OK] Successfully created {stats['relationships_created']} relationships!")

    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch extract relationships from glossary entries")
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.5,
        help="Minimum confidence threshold (0.0-1.0, default: 0.5)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only N entries (default: all)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip entries that already have relationships"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be extracted without saving"
    )

    args = parser.parse_args()

    batch_extract_relationships(
        min_confidence=args.min_confidence,
        limit=args.limit,
        skip_existing=args.skip_existing,
        dry_run=args.dry_run
    )

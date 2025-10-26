"""
Create sample relationships for testing graph visualization
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.relationship import TermRelationship
from datetime import datetime

# Connect to database
database_path = project_root / "data" / "glossary.db"
engine = create_engine(f"sqlite:///{database_path}")
Session = sessionmaker(bind=engine)
session = Session()

# Sample relationships based on domain knowledge
# Format: (source_term_id, target_term_id, relation_type, confidence, evidence)
sample_relationships = [
    # Sensor measures various parameters
    (6, 10, "measures", 0.9, "Sensor measures measurement", "Sensors are used for measurement"),
    (6, 1, "measures", 0.85, "Sensor measures time", "Time measurement using sensors"),

    # Bioreactor relationships
    (5, 3, "uses", 0.9, "Bioreactor uses reactor", "A bioreactor is a type of reactor"),
    (5, 6, "uses", 0.85, "Bioreactor uses sensor", "Bioreactors use sensors for monitoring"),
    (5, 4, "controls", 0.8, "Bioreactor controls process", "Bioreactor controls the process"),

    # Process relationships
    (4, 2, "uses", 0.85, "Process uses method", "Process uses methodologies"),
    (4, 10, "requires", 0.8, "Process requires measurement", "Process requires measurements"),

    # Method relationships
    (2, 10, "enables", 0.75, "Method enables measurement", "Methods enable measurements"),
    (2, 1, "requires", 0.7, "Method requires time", "Methods require time"),

    # Measurement relationships
    (10, 6, "requires", 0.85, "Measurement requires sensor", "Measurements require sensors"),
]

print("Creating sample relationships...")
print("=" * 60)

created = 0
skipped = 0

for source_id, target_id, rel_type, confidence, evidence, context in sample_relationships:
    # Check if relationship already exists
    existing = session.query(TermRelationship).filter(
        TermRelationship.source_term_id == source_id,
        TermRelationship.target_term_id == target_id,
        TermRelationship.relation_type == rel_type
    ).first()

    if existing:
        print(f"SKIP: {source_id} -> {target_id} ({rel_type}) - already exists")
        skipped += 1
        continue

    # Create relationship
    rel = TermRelationship(
        source_term_id=source_id,
        target_term_id=target_id,
        relation_type=rel_type,
        confidence=confidence,
        evidence=evidence,
        context=context,
        extraction_method="manual_sample",
        validated="validated"
    )

    session.add(rel)
    print(f"CREATE: {source_id} -> {target_id} ({rel_type}, confidence={confidence})")
    created += 1

session.commit()

print("=" * 60)
print(f"\nSummary:")
print(f"  Created: {created}")
print(f"  Skipped: {skipped}")
print(f"  Total: {created + skipped}")
print(f"\n[OK] Sample relationships created successfully!")

session.close()

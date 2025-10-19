"""
Database models for term relationships

Stores semantic relationships extracted between glossary terms.
Supports directed graphs with weighted edges and metadata.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship as sqlalchemy_relationship
from datetime import datetime
# Import Base from base_models.py (renamed to avoid conflict with models/ directory)
from ..base_models import Base


class TermRelationship(Base):
    """
    Semantic relationship between two glossary terms

    Represents directed edges in a knowledge graph:
    source_term --[relation_type]--> target_term

    Examples:
    - "temperature sensor" --[MEASURES]--> "temperature"
    - "control system" --[USES]--> "sensor data"
    - "heating element" --[PART_OF]--> "HVAC system"
    """

    __tablename__ = "term_relationships"

    id = Column(Integer, primary_key=True, index=True)

    # Source and target terms (foreign keys to glossary_entries)
    source_term_id = Column(Integer, ForeignKey("glossary_entries.id", ondelete="CASCADE"), nullable=False)
    target_term_id = Column(Integer, ForeignKey("glossary_entries.id", ondelete="CASCADE"), nullable=False)

    # Relationship type
    relation_type = Column(String(50), nullable=False, index=True)
    # Values: uses, measures, part_of, produces, affects, requires, controls, defines, related_to

    # Confidence and evidence
    confidence = Column(Float, nullable=False, default=0.5)
    # 0.0 - 1.0, where 1.0 is highest confidence

    evidence = Column(Text, nullable=True)
    # The specific phrase/pattern that triggered this relationship
    # e.g., "temperature sensor measures temperature"

    context = Column(Text, nullable=True)
    # Full sentence/paragraph where relationship was found

    # Metadata
    extraction_method = Column(String(50), nullable=True)
    # Values: dependency_parsing, pattern_matching, manual, imported

    validated = Column(String(20), nullable=False, default="pending")
    # Values: pending, validated, rejected (for human review)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships to glossary entries
    source_term = sqlalchemy_relationship(
        "GlossaryEntry",
        foreign_keys=[source_term_id],
        backref="outgoing_relationships"
    )
    target_term = sqlalchemy_relationship(
        "GlossaryEntry",
        foreign_keys=[target_term_id],
        backref="incoming_relationships"
    )

    # Indexes for performance
    __table_args__ = (
        Index('idx_source_target', 'source_term_id', 'target_term_id'),
        Index('idx_relation_type', 'relation_type'),
        Index('idx_confidence', 'confidence'),
        Index('idx_validated', 'validated'),
    )

    def __repr__(self):
        return (
            f"<TermRelationship("
            f"source={self.source_term_id}, "
            f"target={self.target_term_id}, "
            f"type={self.relation_type}, "
            f"confidence={self.confidence:.2f})>"
        )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "source_term_id": self.source_term_id,
            "source_term": self.source_term.term if self.source_term else None,
            "target_term_id": self.target_term_id,
            "target_term": self.target_term.term if self.target_term else None,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "context": self.context,
            "extraction_method": self.extraction_method,
            "validated": self.validated,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_graph_edge(self):
        """Convert to graph edge format for visualization"""
        return {
            "id": f"edge-{self.id}",
            "source": self.source_term_id,
            "target": self.target_term_id,
            "type": self.relation_type,
            "weight": self.confidence,
            "label": self.relation_type.replace('_', ' ').title(),
        }

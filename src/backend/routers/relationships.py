"""
API endpoints for term relationships

Provides CRUD operations and graph data retrieval for
semantic relationships between glossary terms.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..database import get_db
from ..models.relationship import TermRelationship
from ..models.glossary_entry import GlossaryEntry
from ..nlp.relationship_extractor import RelationshipExtractor, RelationType


router = APIRouter(prefix="/api/relationships", tags=["relationships"])


# Pydantic schemas
class RelationshipCreate(BaseModel):
    """Schema for creating a new relationship"""
    source_term_id: int = Field(..., description="ID of the source term")
    target_term_id: int = Field(..., description="ID of the target term")
    relation_type: str = Field(..., description="Type of relationship (uses, measures, etc.)")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    evidence: Optional[str] = Field(None, description="Evidence phrase")
    context: Optional[str] = Field(None, description="Full context sentence")
    extraction_method: Optional[str] = Field("manual", description="How relationship was extracted")


class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship"""
    relation_type: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence: Optional[str] = None
    context: Optional[str] = None
    validated: Optional[str] = Field(None, pattern="^(pending|validated|rejected)$")


class RelationshipResponse(BaseModel):
    """Schema for relationship response"""
    id: int
    source_term_id: int
    source_term: Optional[str]
    target_term_id: int
    target_term: Optional[str]
    relation_type: str
    confidence: float
    evidence: Optional[str]
    context: Optional[str]
    extraction_method: Optional[str]
    validated: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GraphNode(BaseModel):
    """Graph node for visualization"""
    id: int
    label: str
    term: str
    language: str
    definition_count: int
    group: Optional[str] = None  # For grouping by domain


class GraphEdge(BaseModel):
    """Graph edge for visualization"""
    id: str
    source: int
    target: int
    type: str
    weight: float
    label: str


class GraphData(BaseModel):
    """Complete graph data for visualization"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: dict


# API Endpoints

@router.post("/", response_model=RelationshipResponse, status_code=201)
def create_relationship(
    relationship: RelationshipCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new term relationship

    Manually add a semantic relationship between two terms.
    """
    # Validate source and target terms exist
    source = db.query(GlossaryEntry).filter(GlossaryEntry.id == relationship.source_term_id).first()
    target = db.query(GlossaryEntry).filter(GlossaryEntry.id == relationship.target_term_id).first()

    if not source:
        raise HTTPException(status_code=404, detail=f"Source term {relationship.source_term_id} not found")
    if not target:
        raise HTTPException(status_code=404, detail=f"Target term {relationship.target_term_id} not found")

    # Prevent self-relationships
    if relationship.source_term_id == relationship.target_term_id:
        raise HTTPException(status_code=400, detail="Cannot create relationship from term to itself")

    # Check for duplicates
    existing = db.query(TermRelationship).filter(
        TermRelationship.source_term_id == relationship.source_term_id,
        TermRelationship.target_term_id == relationship.target_term_id,
        TermRelationship.relation_type == relationship.relation_type
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Relationship already exists (ID: {existing.id})"
        )

    # Create relationship
    db_relationship = TermRelationship(**relationship.dict())
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)

    return db_relationship


@router.get("/", response_model=List[RelationshipResponse])
def get_relationships(
    term_id: Optional[int] = Query(None, description="Filter by term ID (source or target)"),
    source_term_id: Optional[int] = Query(None, description="Filter by source term ID"),
    target_term_id: Optional[int] = Query(None, description="Filter by target term ID"),
    relation_type: Optional[str] = Query(None, description="Filter by relationship type"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence"),
    validated: Optional[str] = Query(None, description="Filter by validation status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get relationships with optional filtering

    Can filter by:
    - term_id: Relationships where term is source OR target
    - source_term_id: Outgoing relationships from term
    - target_term_id: Incoming relationships to term
    - relation_type: Type of relationship
    - min_confidence: Minimum confidence threshold
    - validated: Validation status
    """
    query = db.query(TermRelationship)

    # Apply filters
    if term_id is not None:
        query = query.filter(
            (TermRelationship.source_term_id == term_id) |
            (TermRelationship.target_term_id == term_id)
        )

    if source_term_id is not None:
        query = query.filter(TermRelationship.source_term_id == source_term_id)

    if target_term_id is not None:
        query = query.filter(TermRelationship.target_term_id == target_term_id)

    if relation_type:
        query = query.filter(TermRelationship.relation_type == relation_type)

    if min_confidence > 0.0:
        query = query.filter(TermRelationship.confidence >= min_confidence)

    if validated:
        query = query.filter(TermRelationship.validated == validated)

    # Order by confidence descending
    query = query.order_by(TermRelationship.confidence.desc())

    # Pagination
    total = query.count()
    relationships = query.offset(offset).limit(limit).all()

    return relationships


@router.get("/{relationship_id}", response_model=RelationshipResponse)
def get_relationship(relationship_id: int, db: Session = Depends(get_db)):
    """Get a specific relationship by ID"""
    relationship = db.query(TermRelationship).filter(TermRelationship.id == relationship_id).first()

    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return relationship


@router.put("/{relationship_id}", response_model=RelationshipResponse)
def update_relationship(
    relationship_id: int,
    updates: RelationshipUpdate,
    db: Session = Depends(get_db)
):
    """Update a relationship"""
    relationship = db.query(TermRelationship).filter(TermRelationship.id == relationship_id).first()

    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    # Apply updates
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(relationship, field, value)

    db.commit()
    db.refresh(relationship)

    return relationship


@router.delete("/{relationship_id}", status_code=204)
def delete_relationship(relationship_id: int, db: Session = Depends(get_db)):
    """Delete a relationship"""
    relationship = db.query(TermRelationship).filter(TermRelationship.id == relationship_id).first()

    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    db.delete(relationship)
    db.commit()

    return None


@router.get("/graph/data", response_model=GraphData)
def get_graph_data(
    term_ids: Optional[List[int]] = Query(None, description="Filter to specific terms"),
    relation_types: Optional[List[str]] = Query(None, description="Filter to specific relationship types"),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum confidence"),
    validated_only: bool = Query(False, description="Only include validated relationships"),
    max_depth: int = Query(2, ge=1, le=5, description="Maximum relationship depth from starting terms"),
    db: Session = Depends(get_db)
):
    """
    Get graph data for visualization

    Returns nodes (terms) and edges (relationships) suitable for
    D3.js force-directed graph visualization.

    Parameters:
    - term_ids: Start from these specific terms (if None, use all terms)
    - relation_types: Filter to specific relationship types
    - min_confidence: Minimum confidence threshold
    - validated_only: Only include validated relationships
    - max_depth: How many relationship hops to include
    """
    # Build query for relationships
    query = db.query(TermRelationship)

    if min_confidence > 0.0:
        query = query.filter(TermRelationship.confidence >= min_confidence)

    if validated_only:
        query = query.filter(TermRelationship.validated == "validated")

    if relation_types:
        query = query.filter(TermRelationship.relation_type.in_(relation_types))

    relationships = query.all()

    # If term_ids specified, filter to relevant subgraph
    if term_ids:
        # Get all terms within max_depth hops of starting terms
        relevant_term_ids = set(term_ids)
        current_terms = set(term_ids)

        for depth in range(max_depth):
            next_terms = set()
            for rel in relationships:
                if rel.source_term_id in current_terms:
                    next_terms.add(rel.target_term_id)
                    relevant_term_ids.add(rel.target_term_id)
                if rel.target_term_id in current_terms:
                    next_terms.add(rel.source_term_id)
                    relevant_term_ids.add(rel.source_term_id)
            current_terms = next_terms
            if not current_terms:
                break

        # Filter relationships to only those within relevant terms
        relationships = [
            r for r in relationships
            if r.source_term_id in relevant_term_ids and r.target_term_id in relevant_term_ids
        ]
    else:
        # Get all terms that have relationships
        relevant_term_ids = set()
        for rel in relationships:
            relevant_term_ids.add(rel.source_term_id)
            relevant_term_ids.add(rel.target_term_id)

    # Get term data for nodes
    terms = db.query(GlossaryEntry).filter(GlossaryEntry.id.in_(relevant_term_ids)).all()

    # Build nodes
    nodes = []
    for term in terms:
        nodes.append(GraphNode(
            id=term.id,
            label=term.term,
            term=term.term,
            language=term.language or "en",
            definition_count=len(term.definitions) if term.definitions else 0,
            group=term.domain_tags[0] if term.domain_tags else None
        ))

    # Build edges
    edges = []
    for rel in relationships:
        edges.append(GraphEdge(
            id=f"edge-{rel.id}",
            source=rel.source_term_id,
            target=rel.target_term_id,
            type=rel.relation_type,
            weight=rel.confidence,
            label=rel.relation_type.replace('_', ' ').title()
        ))

    # Calculate stats
    stats = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "relationship_types": list(set(e.type for e in edges)),
        "avg_confidence": sum(e.weight for e in edges) / len(edges) if edges else 0.0,
        "max_depth": max_depth,
    }

    return GraphData(nodes=nodes, edges=edges, stats=stats)


@router.post("/extract/{term_id}", response_model=dict)
def extract_relationships_for_term(
    term_id: int,
    min_confidence: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """
    Extract relationships for a specific term using NLP

    Analyzes the term's definitions and extracts semantic relationships
    to other terms in the glossary.
    """
    # Get the term
    term = db.query(GlossaryEntry).filter(GlossaryEntry.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")

    # Get all terms for relationship extraction
    all_terms = db.query(GlossaryEntry).all()
    term_list = [t.term for t in all_terms]

    # Initialize NLP extractor
    try:
        extractor = RelationshipExtractor()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Extract relationships
    definitions = [
        {
            "definition_text": d.get("definition_text", ""),
            "context": d.get("context", "")
        }
        for d in (term.definitions or [])
    ]

    extracted = extractor.extract_from_glossary_entry(
        term.term,
        definitions,
        term_list,
        min_confidence
    )

    # Save to database
    created_count = 0
    skipped_count = 0

    for rel in extracted:
        # Find source and target IDs
        source_id = term.id
        target = db.query(GlossaryEntry).filter(GlossaryEntry.term == rel.target_term).first()

        if not target:
            skipped_count += 1
            continue

        # Check if relationship already exists
        existing = db.query(TermRelationship).filter(
            TermRelationship.source_term_id == source_id,
            TermRelationship.target_term_id == target.id,
            TermRelationship.relation_type == rel.relation_type.value
        ).first()

        if existing:
            skipped_count += 1
            continue

        # Create new relationship
        db_rel = TermRelationship(
            source_term_id=source_id,
            target_term_id=target.id,
            relation_type=rel.relation_type.value,
            confidence=rel.confidence,
            evidence=rel.evidence,
            context=rel.context,
            extraction_method="dependency_parsing" if "dependency" in rel.evidence.lower() else "pattern_matching"
        )
        db.add(db_rel)
        created_count += 1

    db.commit()

    return {
        "term_id": term_id,
        "term": term.term,
        "extracted": len(extracted),
        "created": created_count,
        "skipped": skipped_count,
        "message": f"Extracted {created_count} new relationships for '{term.term}'"
    }


@router.get("/stats/overview", response_model=dict)
def get_relationship_stats(db: Session = Depends(get_db)):
    """Get overall relationship statistics"""
    total = db.query(TermRelationship).count()
    validated = db.query(TermRelationship).filter(TermRelationship.validated == "validated").count()
    pending = db.query(TermRelationship).filter(TermRelationship.validated == "pending").count()
    rejected = db.query(TermRelationship).filter(TermRelationship.validated == "rejected").count()

    # Count by type
    types = db.query(
        TermRelationship.relation_type,
        db.func.count(TermRelationship.id)
    ).group_by(TermRelationship.relation_type).all()

    type_counts = {rel_type: count for rel_type, count in types}

    # Average confidence
    avg_confidence = db.query(db.func.avg(TermRelationship.confidence)).scalar() or 0.0

    return {
        "total_relationships": total,
        "validated": validated,
        "pending": pending,
        "rejected": rejected,
        "by_type": type_counts,
        "avg_confidence": round(avg_confidence, 3),
    }

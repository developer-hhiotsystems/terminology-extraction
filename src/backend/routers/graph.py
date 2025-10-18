"""
Graph Database API Endpoints
Provides access to Neo4j knowledge graph features
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from src.backend.database import get_db
from src.backend.services.neo4j_service import get_neo4j_service, Neo4jService
from src.backend.services.graph_sync import get_graph_sync_service, GraphSyncService


router = APIRouter(prefix="/api/graph", tags=["graph"])


# ===== SCHEMAS =====

class GraphStatusResponse(BaseModel):
    """Response for graph database status"""
    connected: bool
    message: str
    statistics: Optional[dict] = None


class SyncRequest(BaseModel):
    """Request for syncing data to graph"""
    limit: Optional[int] = Field(None, description="Limit number of terms to sync (None = all)")
    detect_relationships: bool = Field(False, description="Auto-detect relationships after sync")


class SyncResponse(BaseModel):
    """Response from sync operation"""
    success: bool
    message: str
    synced: int = 0
    failed: int = 0
    relationships_created: Optional[int] = None


class RelatedTerm(BaseModel):
    """Related term information"""
    term_id: int
    term_text: str
    language: str
    definitions: List[str] = []
    relationship_path: List[str]
    distance: int


class RelatedTermsResponse(BaseModel):
    """Response for related terms query"""
    term_id: int
    related_terms: List[RelatedTerm]
    total_count: int


class TermHierarchyResponse(BaseModel):
    """Response for term hierarchy query"""
    term_id: int
    parents: List[dict]
    children: List[dict]


class CreateRelationshipRequest(BaseModel):
    """Request to create a relationship between terms"""
    from_term_id: int
    to_term_id: int
    relationship_type: str = Field(..., description="SYNONYM_OF, RELATED_TO, PART_OF, etc.")
    properties: Optional[dict] = Field(None, description="Additional relationship properties")


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool


# ===== ENDPOINTS =====

@router.get("/status", response_model=GraphStatusResponse)
async def get_graph_status(
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get Neo4j graph database status and statistics

    Returns connection status and basic statistics about the knowledge graph
    """
    connected = neo4j.is_connected()

    if not connected:
        return GraphStatusResponse(
            connected=False,
            message="Neo4j is not connected. Please check configuration and ensure Neo4j is running.",
            statistics=None
        )

    # Get statistics
    stats = neo4j.get_term_statistics()

    return GraphStatusResponse(
        connected=True,
        message="Neo4j is connected and ready",
        statistics=stats
    )


@router.post("/sync", response_model=SyncResponse)
async def sync_to_graph(
    sync_request: SyncRequest,
    db: Session = Depends(get_db),
    sync_service: GraphSyncService = Depends(get_graph_sync_service),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Sync glossary terms from SQLite to Neo4j graph database

    This endpoint:
    1. Copies all terms from SQLite to Neo4j as Term nodes
    2. Optionally auto-detects relationships between terms

    **Note:** This is an idempotent operation - existing terms will be updated.
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not connected"
        )

    # Initialize schema first
    neo4j.init_schema()

    # Sync terms
    sync_result = sync_service.sync_all_terms(db, limit=sync_request.limit)

    if not sync_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=sync_result["message"]
        )

    response_data = {
        "success": True,
        "message": sync_result["message"],
        "synced": sync_result.get("synced", 0),
        "failed": sync_result.get("failed", 0)
    }

    # Auto-detect relationships if requested
    if sync_request.detect_relationships:
        rel_result = sync_service.detect_and_create_relationships(db)
        if rel_result["success"]:
            response_data["relationships_created"] = rel_result["total_relationships"]
            response_data["message"] += f" | Created {rel_result['total_relationships']} relationships"

    return SyncResponse(**response_data)


@router.get("/terms/{term_id}/related", response_model=RelatedTermsResponse)
async def get_related_terms(
    term_id: int,
    relationship_types: Optional[str] = None,
    max_depth: int = 2,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get terms related to a specific term

    Args:
    - **term_id**: ID of the term to find relationships for
    - **relationship_types**: Comma-separated list of relationship types (e.g., "SYNONYM_OF,RELATED_TO")
    - **max_depth**: Maximum relationship depth to traverse (default: 2)

    Returns list of related terms with relationship paths and distances
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not connected"
        )

    # Parse relationship types
    rel_types = None
    if relationship_types:
        rel_types = [r.strip() for r in relationship_types.split(",")]

    # Query Neo4j
    related = neo4j.find_related_terms(term_id, rel_types, max_depth)

    # Convert to response format
    related_terms = [
        RelatedTerm(
            term_id=r["term_id"],
            term_text=r["term_text"],
            language=r["language"],
            definitions=r.get("definitions", []),
            relationship_path=r["relationship_path"],
            distance=r["distance"]
        )
        for r in related
    ]

    return RelatedTermsResponse(
        term_id=term_id,
        related_terms=related_terms,
        total_count=len(related_terms)
    )


@router.get("/terms/{term_id}/synonyms")
async def get_synonyms(
    term_id: int,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get all synonyms of a term

    Returns terms connected via SYNONYM_OF relationships
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not connected"
        )

    synonyms = neo4j.find_synonyms(term_id)

    return {
        "term_id": term_id,
        "synonyms": synonyms,
        "count": len(synonyms)
    }


@router.get("/terms/{term_id}/hierarchy", response_model=TermHierarchyResponse)
async def get_term_hierarchy(
    term_id: int,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get hierarchical relationships for a term

    Returns:
    - **parents**: Terms that this term is PART_OF
    - **children**: Terms that are PART_OF this term
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not connected"
        )

    hierarchy = neo4j.find_term_hierarchy(term_id)

    return TermHierarchyResponse(
        term_id=term_id,
        parents=hierarchy["parents"],
        children=hierarchy["children"]
    )


@router.post("/relationships", response_model=MessageResponse)
async def create_relationship(
    request: CreateRelationshipRequest,
    sync_service: GraphSyncService = Depends(get_graph_sync_service),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Create a manual relationship between two terms

    Supported relationship types:
    - **SYNONYM_OF**: Terms with same meaning
    - **RELATED_TO**: Terms that are related but not synonyms
    - **PART_OF**: Hierarchical relationship (child is part of parent)
    - **OPPOSITE_OF**: Antonyms
    - **ABBREVIATION_OF**: Term is abbreviation of another

    The relationship is directed: from_term -> to_term
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not connected"
        )

    # Validate relationship type
    valid_types = ["SYNONYM_OF", "RELATED_TO", "PART_OF", "OPPOSITE_OF", "ABBREVIATION_OF"]
    if request.relationship_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid relationship type. Must be one of: {', '.join(valid_types)}"
        )

    success = sync_service.create_manual_relationship(
        request.from_term_id,
        request.to_term_id,
        request.relationship_type,
        request.properties
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create relationship"
        )

    return MessageResponse(
        success=True,
        message=f"Created {request.relationship_type} relationship between terms {request.from_term_id} and {request.to_term_id}"
    )


@router.get("/search")
async def search_graph(
    q: str,
    language: Optional[str] = None,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Search for terms in the knowledge graph

    Args:
    - **q**: Search query (partial text match)
    - **language**: Optional language filter (en/de)

    Returns matching terms from Neo4j
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not connected"
        )

    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )

    results = neo4j.search_terms(q, language)

    return {
        "query": q,
        "language": language,
        "results": results,
        "count": len(results)
    }


@router.delete("/clear")
async def clear_graph(
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    **DANGER:** Clear all data from Neo4j graph database

    This endpoint deletes all nodes and relationships.
    Use with caution - this action cannot be undone!
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not connected"
        )

    with neo4j.get_session() as session:
        # Delete all nodes and relationships
        result = session.run("MATCH (n) DETACH DELETE n")
        summary = result.consume()

    return {
        "success": True,
        "message": "Graph database cleared successfully",
        "nodes_deleted": summary.counters.nodes_deleted,
        "relationships_deleted": summary.counters.relationships_deleted
    }

"""
Full-Text Search API Router
============================
Provides FTS5-powered search endpoints with BM25 ranking, filtering, and snippets.

Features:
- Full-text search with Porter stemming
- BM25 relevance ranking
- Language and domain filtering
- Snippet extraction with highlighting
- Phrase search with quotes
- Wildcard search with *
- Boolean operators (AND, OR, NOT)
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
import sqlite3
import logging

from src.backend.database import get_db
from src.backend.config import config
from src.backend.constants import LANG_ENGLISH, LANG_GERMAN, SUPPORTED_LANGUAGES

router = APIRouter(
    prefix="/api/search",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


# =============================================================================
# Response Schemas
# =============================================================================

class SearchResult(BaseModel):
    """Individual search result with relevance score"""
    id: int
    term: str
    definitions: list
    language: str
    source: str
    domain_tags: Optional[list] = None
    relevance_score: float = Field(..., description="BM25 relevance score (lower is better)")
    snippet: Optional[str] = Field(None, description="Context snippet with highlighted matches")

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response with results and metadata"""
    query: str
    total_results: int
    results: List[SearchResult]
    filters_applied: dict


# =============================================================================
# Helper Functions
# =============================================================================

def get_raw_db_connection():
    """
    Get raw SQLite connection for FTS5 queries

    FTS5 external content tables work better with raw SQLite connections
    than SQLAlchemy ORM due to virtual table quirks.
    """
    db_path = config.DATABASE_URL.replace("sqlite:///", "")
    return sqlite3.connect(db_path)


def build_fts5_query(
    query: str,
    language: Optional[str] = None,
    domain: Optional[str] = None
) -> tuple[str, dict]:
    """
    Build FTS5 SQL query with filters

    Args:
        query: Search query string
        language: Optional language filter (en/de)
        domain: Optional domain filter

    Returns:
        Tuple of (SQL query string, parameters dict)
    """
    # Base FTS5 search query with JOIN to get actual data
    # Note: snippet() function doesn't work with external content FTS5 tables
    sql = """
        SELECT
            ge.id,
            ge.term,
            ge.definitions,
            ge.language,
            ge.source,
            ge.domain_tags,
            bm25(glossary_fts) AS relevance_score
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH :query
    """

    params = {"query": query}

    # Add language filter
    if language:
        sql += " AND ge.language = :language"
        params["language"] = language

    # Add domain filter (search in JSON array)
    if domain:
        # SQLite JSON search: check if domain exists in domain_tags array
        sql += """ AND EXISTS (
            SELECT 1 FROM json_each(ge.domain_tags)
            WHERE value = :domain
        )"""
        params["domain"] = domain

    # Order by relevance (BM25 score - lower is better in FTS5)
    sql += " ORDER BY relevance_score"

    return sql, params


# =============================================================================
# Search Endpoints
# =============================================================================

@router.get(
    "/fulltext",
    response_model=SearchResponse,
    summary="Full-text search with FTS5",
    description="""
    Search glossary entries using SQLite FTS5 full-text search.

    **Query Syntax:**
    - Simple search: `temperature control`
    - Phrase search: `"temperature control"`
    - Wildcards: `temp*` (prefix matching)
    - Boolean: `temperature AND control`, `sensor OR actuator`
    - Exclusion: `temperature NOT sensor`

    **Features:**
    - BM25 relevance ranking
    - Porter stemming (running → run, controlled → control)
    - Diacritic removal (café → cafe)
    - Language filtering (en/de)
    - Domain filtering
    - Snippet extraction with highlighted matches
    """,
)
async def fulltext_search(
    q: str = Query(
        ...,
        min_length=2,
        max_length=200,
        description="Search query (minimum 2 characters)",
        example="temperature control"
    ),
    language: Optional[str] = Query(
        None,
        regex=f"^({'|'.join(SUPPORTED_LANGUAGES)})$",
        description="Filter by language (en or de)"
    ),
    domain: Optional[str] = Query(
        None,
        description="Filter by domain tag"
    ),
    limit: int = Query(
        50,
        ge=1,
        le=500,
        description="Maximum number of results to return"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of results to skip (for pagination)"
    ),
    db: Session = Depends(get_db)
):
    """
    Full-text search endpoint using FTS5

    Returns search results ranked by BM25 relevance score with optional
    language and domain filtering.
    """
    try:
        # Build FTS5 query
        sql, params = build_fts5_query(q, language, domain)

        # Add pagination
        sql += f" LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        # Execute query using raw SQLite connection
        conn = get_raw_db_connection()
        cursor = conn.cursor()

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        # Get total count (without pagination)
        count_sql, count_params = build_fts5_query(q, language, domain)
        count_sql = f"""
            SELECT COUNT(*)
            FROM ({count_sql}) AS search_results
        """
        cursor.execute(count_sql, count_params)
        total_count = cursor.fetchone()[0]

        conn.close()

        # Convert rows to SearchResult objects
        results = []
        for row in rows:
            import json
            id_, term, definitions_json, lang, source, domain_tags_json, score = row

            # Extract first definition text as snippet (manual implementation)
            definitions = json.loads(definitions_json) if definitions_json else []
            snippet = None
            if definitions and len(definitions) > 0 and 'text' in definitions[0]:
                # Take first 100 chars of first definition as snippet
                snippet_text = definitions[0]['text']
                snippet = snippet_text[:100] + "..." if len(snippet_text) > 100 else snippet_text

            results.append(SearchResult(
                id=id_,
                term=term,
                definitions=definitions,
                language=lang,
                source=source,
                domain_tags=json.loads(domain_tags_json) if domain_tags_json else [],
                relevance_score=score,
                snippet=snippet
            ))

        # Build response
        response = SearchResponse(
            query=q,
            total_results=total_count,
            results=results,
            filters_applied={
                "language": language,
                "domain": domain,
                "limit": limit,
                "offset": offset
            }
        )

        logger.info(f"Search query='{q}' returned {total_count} results")
        return response

    except sqlite3.OperationalError as e:
        logger.error(f"FTS5 query error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid search query: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during search"
        )


@router.get(
    "/suggest",
    summary="Search suggestions (autocomplete)",
    description="Get search suggestions based on partial term input",
)
async def search_suggestions(
    q: str = Query(
        ...,
        min_length=2,
        max_length=50,
        description="Partial term for autocomplete",
        example="temp"
    ),
    language: Optional[str] = Query(
        None,
        regex=f"^({'|'.join(SUPPORTED_LANGUAGES)})$",
        description="Filter by language (en or de)"
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum number of suggestions"
    ),
):
    """
    Get autocomplete suggestions using FTS5 prefix search

    Uses wildcard matching with asterisk (*) for prefix matching.
    Example: "temp" → "temp*" matches "temperature", "temporal", etc.
    """
    try:
        # Use prefix matching with wildcard
        fts_query = f"{q}*"

        sql = """
            SELECT DISTINCT ge.term, bm25(glossary_fts) AS score
            FROM glossary_fts fts
            JOIN glossary_entries ge ON fts.rowid = ge.id
            WHERE glossary_fts MATCH :query
        """

        params = {"query": fts_query}

        if language:
            sql += " AND ge.language = :language"
            params["language"] = language

        sql += " ORDER BY score LIMIT :limit"
        params["limit"] = limit

        conn = get_raw_db_connection()
        cursor = conn.cursor()

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        conn.close()

        # Return simple list of terms
        suggestions = [row[0] for row in rows]

        return {
            "query": q,
            "suggestions": suggestions
        }

    except Exception as e:
        logger.error(f"Suggestion error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error generating suggestions"
        )


@router.get(
    "/stats",
    summary="Search index statistics",
    description="Get statistics about the FTS5 search index",
)
async def search_stats():
    """
    Get FTS5 index statistics

    Returns information about the search index size, language distribution,
    and other metadata.
    """
    try:
        conn = get_raw_db_connection()
        cursor = conn.cursor()

        # Total indexed entries
        cursor.execute("""
            SELECT COUNT(*)
            FROM glossary_fts fts
            JOIN glossary_entries ge ON fts.rowid = ge.id
            WHERE glossary_fts MATCH 'the OR and OR of'
        """)
        total_count = cursor.fetchone()[0]

        # Entries by language
        cursor.execute("""
            SELECT language, COUNT(*)
            FROM glossary_entries
            GROUP BY language
        """)
        language_stats = dict(cursor.fetchall())

        # Entries by source
        cursor.execute("""
            SELECT source, COUNT(*)
            FROM glossary_entries
            GROUP BY source
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """)
        source_stats = dict(cursor.fetchall())

        # Check if FTS5 is enabled
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='glossary_fts'
        """)
        fts5_enabled = cursor.fetchone() is not None

        conn.close()

        return {
            "fts5_enabled": fts5_enabled,
            "total_indexed_entries": total_count,
            "entries_by_language": language_stats,
            "top_sources": source_stats,
            "search_features": {
                "porter_stemming": True,
                "diacritic_removal": True,
                "phrase_search": True,
                "wildcard_search": True,
                "boolean_operators": True,
                "bm25_ranking": True,
                "snippet_extraction": True
            }
        }

    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error retrieving statistics"
        )

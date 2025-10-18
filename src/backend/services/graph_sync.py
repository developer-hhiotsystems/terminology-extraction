"""
Graph Sync Service
Synchronizes data between SQLite and Neo4j graph database
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from src.backend.models import GlossaryEntry
from src.backend.services.neo4j_service import get_neo4j_service
import re


class GraphSyncService:
    """Service for synchronizing SQLite data with Neo4j graph"""

    def __init__(self):
        self.neo4j = get_neo4j_service()

    def sync_term_to_graph(self, entry: GlossaryEntry) -> bool:
        """
        Sync a single glossary entry to Neo4j

        Args:
            entry: GlossaryEntry from SQLite

        Returns:
            True if successful, False otherwise
        """
        if not self.neo4j.is_connected():
            return False

        # Prepare term data for Neo4j
        # Handle definitions - could be JSON array or single text
        definitions = []
        if hasattr(entry, 'definitions') and entry.definitions:
            if isinstance(entry.definitions, list):
                definitions = [d.get('text', '') for d in entry.definitions if isinstance(d, dict)]
            else:
                definitions = [str(entry.definitions)]
        elif hasattr(entry, 'definition') and entry.definition:
            definitions = [entry.definition]

        term_data = {
            "term_id": entry.id,
            "term_text": entry.term,
            "language": entry.language or "en",
            "definitions": definitions,
            "domain_tags": entry.domain_tags or [],
            "source": entry.source or "unknown"
        }

        return self.neo4j.create_or_update_term(term_data)

    def sync_all_terms(self, db: Session, limit: Optional[int] = None) -> dict:
        """
        Sync all glossary entries from SQLite to Neo4j

        Args:
            db: SQLAlchemy database session
            limit: Optional limit on number of terms to sync

        Returns:
            Dictionary with sync statistics
        """
        if not self.neo4j.is_connected():
            return {
                "success": False,
                "message": "Neo4j not connected",
                "synced": 0,
                "failed": 0
            }

        query = db.query(GlossaryEntry)
        if limit:
            query = query.limit(limit)

        entries = query.all()
        synced = 0
        failed = 0

        for entry in entries:
            if self.sync_term_to_graph(entry):
                synced += 1
            else:
                failed += 1

        return {
            "success": True,
            "message": f"Synced {synced} terms to Neo4j",
            "synced": synced,
            "failed": failed,
            "total": len(entries)
        }

    def detect_and_create_relationships(self, db: Session, batch_size: int = 100) -> dict:
        """
        Auto-detect and create relationships between terms

        This creates:
        - SYNONYM_OF relationships (based on similar definitions)
        - RELATED_TO relationships (based on shared domain tags)
        - PART_OF relationships (based on term patterns like "X valve" -> "valve")

        Args:
            db: SQLAlchemy database session
            batch_size: Number of terms to process at once

        Returns:
            Dictionary with relationship statistics
        """
        if not self.neo4j.is_connected():
            return {
                "success": False,
                "message": "Neo4j not connected"
            }

        entries = db.query(GlossaryEntry).limit(batch_size).all()

        synonym_count = 0
        related_count = 0
        hierarchy_count = 0

        # Process each term
        for i, entry in enumerate(entries):
            # 1. Find potential synonyms (same language, similar term)
            for other in entries[i+1:]:
                if entry.language == other.language:
                    # Check if terms are very similar (potential synonyms)
                    if self._are_similar_terms(entry.term, other.term):
                        if self.neo4j.create_relationship(
                            entry.id, other.id, "SYNONYM_OF",
                            {"confidence": 0.8, "auto_detected": True}
                        ):
                            synonym_count += 1

            # 2. Find related terms (shared domain tags)
            if entry.domain_tags:
                for other in entries:
                    if entry.id != other.id and other.domain_tags:
                        shared_tags = set(entry.domain_tags) & set(other.domain_tags)
                        if len(shared_tags) >= 2:  # At least 2 shared tags
                            if self.neo4j.create_relationship(
                                entry.id, other.id, "RELATED_TO",
                                {
                                    "shared_tags": list(shared_tags),
                                    "auto_detected": True
                                }
                            ):
                                related_count += 1

            # 3. Detect hierarchical relationships (compound terms)
            parent_term = self._extract_parent_term(entry.term)
            if parent_term:
                # Find the parent term in database
                parent_entry = db.query(GlossaryEntry).filter(
                    GlossaryEntry.term.ilike(parent_term),
                    GlossaryEntry.language == entry.language
                ).first()

                if parent_entry:
                    if self.neo4j.create_relationship(
                        entry.id, parent_entry.id, "PART_OF",
                        {"auto_detected": True}
                    ):
                        hierarchy_count += 1

        return {
            "success": True,
            "synonyms_created": synonym_count,
            "related_created": related_count,
            "hierarchy_created": hierarchy_count,
            "total_relationships": synonym_count + related_count + hierarchy_count
        }

    def _are_similar_terms(self, term1: str, term2: str) -> bool:
        """
        Check if two terms are similar (potential synonyms)

        Uses simple string similarity - could be enhanced with Levenshtein distance
        """
        # Normalize
        t1 = term1.lower().strip()
        t2 = term2.lower().strip()

        # Exact match after normalization
        if t1 == t2:
            return True

        # Check if one is substring of other (e.g., "valve" and "safety valve")
        if t1 in t2 or t2 in t1:
            return False  # These are more hierarchical than synonyms

        # Check for very similar length and characters
        if abs(len(t1) - len(t2)) <= 2:
            # Simple character overlap check
            chars1 = set(t1.replace(" ", ""))
            chars2 = set(t2.replace(" ", ""))
            overlap = len(chars1 & chars2)
            max_chars = max(len(chars1), len(chars2))

            if overlap / max_chars > 0.8:  # 80% character overlap
                return True

        return False

    def _extract_parent_term(self, term: str) -> Optional[str]:
        """
        Extract parent term from compound terms

        Examples:
        - "Safety Valve" -> "Valve"
        - "Pressure Sensor" -> "Sensor"
        - "Bioreactor System" -> "System" or "Bioreactor"
        """
        words = term.split()

        if len(words) < 2:
            return None

        # Return the last word as potential parent
        # (e.g., "Safety Valve" -> "Valve")
        return words[-1]

    def create_manual_relationship(
        self,
        from_term_id: int,
        to_term_id: int,
        relationship_type: str,
        properties: Optional[dict] = None
    ) -> bool:
        """
        Create a manual (user-defined) relationship between terms

        Args:
            from_term_id: Source term ID
            to_term_id: Target term ID
            relationship_type: Type (SYNONYM_OF, RELATED_TO, PART_OF, etc.)
            properties: Additional properties

        Returns:
            True if successful
        """
        if not self.neo4j.is_connected():
            return False

        props = properties or {}
        props["auto_detected"] = False  # Mark as manual

        return self.neo4j.create_relationship(
            from_term_id, to_term_id, relationship_type, props
        )


# Global sync service instance
graph_sync_service = GraphSyncService()


def get_graph_sync_service() -> GraphSyncService:
    """Dependency injection for graph sync service"""
    return graph_sync_service

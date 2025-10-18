"""
Neo4j Graph Database Service
Manages connection and operations with Neo4j for term relationships
"""
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: Neo4j driver not installed. Run: pip install neo4j")


class Neo4jService:
    """Service for managing Neo4j graph database operations"""

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "devpassword")
        self.driver: Optional[Driver] = None
        self._connected = False

        if NEO4J_AVAILABLE:
            self._init_connection()

    def _init_connection(self):
        """Initialize connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            self.driver.verify_connectivity()
            self._connected = True
            print(f"✓ Connected to Neo4j at {self.uri}")
        except Exception as e:
            self._connected = False
            print(f"⚠ Neo4j connection failed: {str(e)}")
            print("  Neo4j features will be disabled")

    @contextmanager
    def get_session(self):
        """Context manager for Neo4j sessions"""
        if not self._connected or not self.driver:
            raise RuntimeError("Neo4j not connected")

        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

    def is_connected(self) -> bool:
        """Check if Neo4j is connected and available"""
        return self._connected and NEO4J_AVAILABLE

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self._connected = False
            print("✓ Neo4j connection closed")

    # ===== SCHEMA SETUP =====

    def init_schema(self):
        """Initialize Neo4j schema with constraints and indexes"""
        if not self.is_connected():
            return False

        with self.get_session() as session:
            # Create unique constraint on Term.term_id
            session.run("""
                CREATE CONSTRAINT term_id_unique IF NOT EXISTS
                FOR (t:Term) REQUIRE t.term_id IS UNIQUE
            """)

            # Create unique constraint on Document.document_id
            session.run("""
                CREATE CONSTRAINT document_id_unique IF NOT EXISTS
                FOR (d:Document) REQUIRE d.document_id IS UNIQUE
            """)

            # Create index on Term.term_text for faster searches
            session.run("""
                CREATE INDEX term_text_index IF NOT EXISTS
                FOR (t:Term) ON (t.term_text)
            """)

            # Create index on Term.language
            session.run("""
                CREATE INDEX term_language_index IF NOT EXISTS
                FOR (t:Term) ON (t.language)
            """)

            print("✓ Neo4j schema initialized")
            return True

    # ===== TERM OPERATIONS =====

    def create_or_update_term(self, term_data: Dict[str, Any]) -> bool:
        """
        Create or update a term node in Neo4j

        Args:
            term_data: Dictionary with term information
                - term_id: int (required)
                - term_text: str (required)
                - language: str (required)
                - definitions: list (optional)
                - domain_tags: list (optional)
                - source: str (optional)
        """
        if not self.is_connected():
            return False

        with self.get_session() as session:
            session.run("""
                MERGE (t:Term {term_id: $term_id})
                SET t.term_text = $term_text,
                    t.language = $language,
                    t.definitions = $definitions,
                    t.domain_tags = $domain_tags,
                    t.source = $source,
                    t.updated_at = datetime()
            """, term_data)

            return True

    def create_relationship(
        self,
        from_term_id: int,
        to_term_id: int,
        relationship_type: str,
        properties: Optional[Dict] = None
    ) -> bool:
        """
        Create a relationship between two terms

        Args:
            from_term_id: Source term ID
            to_term_id: Target term ID
            relationship_type: Type of relationship (SYNONYM_OF, RELATED_TO, PART_OF, etc.)
            properties: Additional properties for the relationship
        """
        if not self.is_connected():
            return False

        props = properties or {}

        with self.get_session() as session:
            query = f"""
                MATCH (from:Term {{term_id: $from_id}})
                MATCH (to:Term {{term_id: $to_id}})
                MERGE (from)-[r:{relationship_type}]->(to)
                SET r += $properties
                SET r.created_at = coalesce(r.created_at, datetime())
                RETURN r
            """

            result = session.run(query, {
                "from_id": from_term_id,
                "to_id": to_term_id,
                "properties": props
            })

            return result.single() is not None

    # ===== QUERY OPERATIONS =====

    def find_related_terms(
        self,
        term_id: int,
        relationship_types: Optional[List[str]] = None,
        max_depth: int = 2
    ) -> List[Dict]:
        """
        Find terms related to a given term

        Args:
            term_id: Term ID to find relationships for
            relationship_types: List of relationship types to consider (None = all)
            max_depth: Maximum depth to traverse (default: 2)

        Returns:
            List of related terms with relationship information
        """
        if not self.is_connected():
            return []

        # Build relationship type filter
        rel_filter = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            rel_filter = f":{rel_types}"

        with self.get_session() as session:
            query = f"""
                MATCH path = (start:Term {{term_id: $term_id}})-[r{rel_filter}*1..{max_depth}]-(related:Term)
                WHERE start <> related
                RETURN DISTINCT
                    related.term_id AS term_id,
                    related.term_text AS term_text,
                    related.language AS language,
                    related.definitions AS definitions,
                    [rel in relationships(path) | type(rel)] AS relationship_path,
                    length(path) AS distance
                ORDER BY distance, related.term_text
                LIMIT 50
            """

            result = session.run(query, {"term_id": term_id})

            return [dict(record) for record in result]

    def find_synonyms(self, term_id: int) -> List[Dict]:
        """Find all synonyms of a term"""
        return self.find_related_terms(
            term_id,
            relationship_types=["SYNONYM_OF"],
            max_depth=3  # Allow transitive synonyms
        )

    def find_term_hierarchy(self, term_id: int) -> Dict:
        """
        Find hierarchical relationships (parents and children)

        Returns:
            Dictionary with 'parents' and 'children' lists
        """
        if not self.is_connected():
            return {"parents": [], "children": []}

        with self.get_session() as session:
            # Find parents (terms this term is PART_OF)
            parents_query = """
                MATCH (child:Term {term_id: $term_id})-[:PART_OF]->(parent:Term)
                RETURN parent.term_id AS term_id,
                       parent.term_text AS term_text,
                       parent.language AS language
            """

            parents_result = session.run(parents_query, {"term_id": term_id})
            parents = [dict(record) for record in parents_result]

            # Find children (terms that are PART_OF this term)
            children_query = """
                MATCH (child:Term)-[:PART_OF]->(parent:Term {term_id: $term_id})
                RETURN child.term_id AS term_id,
                       child.term_text AS term_text,
                       child.language AS language
            """

            children_result = session.run(children_query, {"term_id": term_id})
            children = [dict(record) for record in children_result]

            return {
                "parents": parents,
                "children": children
            }

    def search_terms(self, search_text: str, language: Optional[str] = None) -> List[Dict]:
        """
        Search for terms by text (case-insensitive partial match)

        Args:
            search_text: Text to search for
            language: Optional language filter

        Returns:
            List of matching terms
        """
        if not self.is_connected():
            return []

        with self.get_session() as session:
            query = """
                MATCH (t:Term)
                WHERE toLower(t.term_text) CONTAINS toLower($search_text)
            """

            if language:
                query += " AND t.language = $language"

            query += """
                RETURN t.term_id AS term_id,
                       t.term_text AS term_text,
                       t.language AS language,
                       t.definitions AS definitions,
                       t.domain_tags AS domain_tags
                ORDER BY t.term_text
                LIMIT 100
            """

            params = {"search_text": search_text}
            if language:
                params["language"] = language

            result = session.run(query, params)
            return [dict(record) for record in result]

    def get_term_statistics(self) -> Dict:
        """Get statistics about terms and relationships in the graph"""
        if not self.is_connected():
            return {
                "total_terms": 0,
                "total_relationships": 0,
                "relationship_counts": {},
                "language_distribution": {}
            }

        with self.get_session() as session:
            # Count total terms
            total_terms = session.run("MATCH (t:Term) RETURN count(t) AS count").single()["count"]

            # Count total relationships
            total_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]

            # Count relationships by type
            rel_counts_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS rel_type, count(r) AS count
                ORDER BY count DESC
            """)
            rel_counts = {record["rel_type"]: record["count"] for record in rel_counts_result}

            # Language distribution
            lang_dist_result = session.run("""
                MATCH (t:Term)
                RETURN t.language AS language, count(t) AS count
                ORDER BY count DESC
            """)
            lang_dist = {record["language"]: record["count"] for record in lang_dist_result}

            return {
                "total_terms": total_terms,
                "total_relationships": total_rels,
                "relationship_counts": rel_counts,
                "language_distribution": lang_dist
            }


# Global Neo4j service instance
neo4j_service = Neo4jService()


def get_neo4j_service() -> Neo4jService:
    """Dependency injection for Neo4j service"""
    return neo4j_service

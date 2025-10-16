"""
Integration tests for database connectivity
Note: Python 3.13 has compatibility issues with SQLAlchemy 2.0.23
"""
import pytest
from pathlib import Path

def test_neo4j_driver_import():
    """Test that neo4j driver is importable"""
    from neo4j import GraphDatabase
    assert GraphDatabase

def test_config_exists():
    """Test that config module exists and is accessible"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "backend"))
    from config import config
    assert config.DATABASE_URL
    assert config.NEO4J_URI

@pytest.mark.skip(reason="Requires Neo4j to be running")
def test_neo4j_connection():
    """Test Neo4j connection (requires running database)"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "backend"))

    from neo4j import GraphDatabase
    from config import config

    driver = GraphDatabase.driver(
        config.NEO4J_URI,
        auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
    )

    try:
        driver.verify_connectivity()
        assert True
    finally:
        driver.close()

# TODO Phase 1: Fix SQLAlchemy compatibility with Python 3.13
# OR: Consider downgrading to Python 3.11/3.12 for better compatibility
# TODO Phase 1: Implement full database integration tests

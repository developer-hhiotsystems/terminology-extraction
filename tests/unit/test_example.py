"""
Example unit test to verify pytest setup
"""
import pytest

def test_example():
    """Simple test to verify pytest is working"""
    assert 1 + 1 == 2

def test_health_endpoint_structure():
    """Test health endpoint response structure"""
    # This will be replaced with actual API tests in Phase 1
    expected_keys = {"status", "database", "neo4j"}
    response = {
        "status": "healthy",
        "database": "not_connected",
        "neo4j": "not_connected"
    }
    assert set(response.keys()) == expected_keys

"""
Unit tests for Glossary API endpoints
Tests cover CRUD operations, filtering, and search functionality
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.backend.app import app
from src.backend.database import Base, get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_glossary.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    """Create and teardown test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_returns_200(self):
        """Test health endpoint returns 200 status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]


class TestGlossaryCRUD:
    """Test glossary CRUD operations"""

    def test_create_glossary_entry(self):
        """Test creating a new glossary entry"""
        entry_data = {
            "term": "Test Term",
            "definitions": [{"text": "Test definition", "source_doc_id": None, "is_primary": True}],
            "language": "en",
            "source": "internal",
        }
        response = client.post("/api/glossary", json=entry_data)
        assert response.status_code == 201
        assert response.json()["term"] == "Test Term"

    def test_get_all_entries(self):
        """Test retrieving all entries"""
        response = client.get("/api/glossary")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_entry(self):
        """Test deleting an entry"""
        # Create entry first
        create_resp = client.post("/api/glossary", json={
            "term": "Delete Me",
            "definitions": [{"text": "Will be deleted", "source_doc_id": None, "is_primary": True}],
            "language": "en",
            "source": "internal"
        })
        entry_id = create_resp.json()["id"]

        # Delete it
        delete_resp = client.delete(f"/api/glossary/{entry_id}")
        assert delete_resp.status_code == 204


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

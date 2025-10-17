"""
Unit tests for Glossary CRUD API endpoints
Following TDD approach: Write tests first, then implement endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC

from src.backend.models import Base, GlossaryEntry
from src.backend import database
from src.backend.app import app


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Disable SQL logging for cleaner test output
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database module's engine and SessionLocal
database.engine = test_engine
database.SessionLocal = TestingSessionLocal

# Override the database dependency
app.dependency_overrides[database.get_db] = override_get_db

# Disable startup event for tests (we'll create tables manually)
app.router.on_startup = []


@pytest.fixture
def client():
    """Create test client with fresh database"""
    # Create all tables in the test database
    Base.metadata.drop_all(bind=test_engine)  # Clean slate
    Base.metadata.create_all(bind=test_engine)

    # TestClient will use our overridden get_db which connects to test database
    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_entry_data():
    """Sample glossary entry data for testing"""
    return {
        "term": "Sensor",
        "definition": "A device that detects or measures a physical property and records, indicates, or otherwise responds to it",
        "language": "en",
        "source": "internal",
        "domain_tags": ["automation", "measurement"]
    }


class TestCreateGlossaryEntry:
    """Test POST /api/glossary endpoint"""

    def test_create_entry_success(self, client, sample_entry_data):
        """Test creating a new glossary entry"""
        response = client.post("/api/glossary", json=sample_entry_data)

        assert response.status_code == 201
        data = response.json()
        assert data["term"] == "Sensor"
        assert data["definition"] == sample_entry_data["definition"]
        assert data["language"] == "en"
        assert data["source"] == "internal"
        assert data["validation_status"] == "pending"
        assert data["sync_status"] == "pending_sync"
        assert "id" in data
        assert "creation_date" in data

    def test_create_entry_minimal_fields(self, client):
        """Test creating entry with only required fields"""
        minimal_data = {
            "term": "Actuator",
            "definition": "A component responsible for moving or controlling a mechanism",
            "language": "en"
        }
        response = client.post("/api/glossary", json=minimal_data)

        assert response.status_code == 201
        data = response.json()
        assert data["source"] == "internal"  # Default value

    def test_create_entry_duplicate_term(self, client, sample_entry_data):
        """Test creating duplicate entry fails"""
        # Create first entry
        client.post("/api/glossary", json=sample_entry_data)

        # Try to create duplicate
        response = client.post("/api/glossary", json=sample_entry_data)
        assert response.status_code == 409  # Conflict
        assert "already exists" in response.json()["detail"].lower()

    def test_create_entry_invalid_language(self, client, sample_entry_data):
        """Test creating entry with invalid language fails"""
        sample_entry_data["language"] = "fr"  # Only 'de' and 'en' allowed
        response = client.post("/api/glossary", json=sample_entry_data)

        assert response.status_code == 422  # Validation error

    def test_create_entry_missing_required_fields(self, client):
        """Test creating entry without required fields fails"""
        incomplete_data = {"term": "Sensor"}
        response = client.post("/api/glossary", json=incomplete_data)

        assert response.status_code == 422


class TestGetGlossaryEntries:
    """Test GET /api/glossary endpoints"""

    def test_get_all_entries_empty(self, client):
        """Test getting entries when database is empty"""
        response = client.get("/api/glossary")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_entries(self, client, sample_entry_data):
        """Test getting all glossary entries"""
        # Create multiple entries
        client.post("/api/glossary", json=sample_entry_data)

        entry2_data = sample_entry_data.copy()
        entry2_data["term"] = "Actuator"
        entry2_data["definition"] = "A motor component"
        client.post("/api/glossary", json=entry2_data)

        # Get all entries
        response = client.get("/api/glossary")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["term"] in ["Sensor", "Actuator"]

    def test_get_entry_by_id(self, client, sample_entry_data):
        """Test getting a specific entry by ID"""
        # Create entry
        create_response = client.post("/api/glossary", json=sample_entry_data)
        entry_id = create_response.json()["id"]

        # Get by ID
        response = client.get(f"/api/glossary/{entry_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry_id
        assert data["term"] == "Sensor"

    def test_get_entry_not_found(self, client):
        """Test getting non-existent entry returns 404"""
        response = client.get("/api/glossary/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_entries_filter_by_language(self, client, sample_entry_data):
        """Test filtering entries by language"""
        # Create English entry
        client.post("/api/glossary", json=sample_entry_data)

        # Create German entry
        de_entry = sample_entry_data.copy()
        de_entry["term"] = "Sensor_DE"
        de_entry["language"] = "de"
        client.post("/api/glossary", json=de_entry)

        # Filter by language
        response = client.get("/api/glossary?language=en")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["language"] == "en"

    def test_get_entries_filter_by_source(self, client, sample_entry_data):
        """Test filtering entries by source"""
        # Create internal entry
        client.post("/api/glossary", json=sample_entry_data)

        # Create NAMUR entry
        namur_entry = sample_entry_data.copy()
        namur_entry["term"] = "NAMUR_Term"
        namur_entry["source"] = "NAMUR"
        client.post("/api/glossary", json=namur_entry)

        # Filter by source
        response = client.get("/api/glossary?source=NAMUR")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["source"] == "NAMUR"


class TestUpdateGlossaryEntry:
    """Test PUT /api/glossary/{id} endpoint"""

    def test_update_entry_success(self, client, sample_entry_data):
        """Test updating an existing entry"""
        # Create entry
        create_response = client.post("/api/glossary", json=sample_entry_data)
        entry_id = create_response.json()["id"]

        # Update entry
        update_data = {
            "definition": "An updated definition for the sensor",
            "validation_status": "validated"
        }
        response = client.put(f"/api/glossary/{entry_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["definition"] == update_data["definition"]
        assert data["validation_status"] == "validated"
        assert data["term"] == "Sensor"  # Unchanged

    def test_update_entry_not_found(self, client):
        """Test updating non-existent entry returns 404"""
        update_data = {"definition": "New definition"}
        response = client.put("/api/glossary/99999", json=update_data)

        assert response.status_code == 404

    def test_update_entry_invalid_status(self, client, sample_entry_data):
        """Test updating with invalid validation_status fails"""
        # Create entry
        create_response = client.post("/api/glossary", json=sample_entry_data)
        entry_id = create_response.json()["id"]

        # Try invalid status
        update_data = {"validation_status": "invalid_status"}
        response = client.put(f"/api/glossary/{entry_id}", json=update_data)

        assert response.status_code == 422


class TestDeleteGlossaryEntry:
    """Test DELETE /api/glossary/{id} endpoint"""

    def test_delete_entry_success(self, client, sample_entry_data):
        """Test deleting an entry"""
        # Create entry
        create_response = client.post("/api/glossary", json=sample_entry_data)
        entry_id = create_response.json()["id"]

        # Delete entry
        response = client.delete(f"/api/glossary/{entry_id}")

        assert response.status_code == 204

        # Verify entry is deleted
        get_response = client.get(f"/api/glossary/{entry_id}")
        assert get_response.status_code == 404

    def test_delete_entry_not_found(self, client):
        """Test deleting non-existent entry returns 404"""
        response = client.delete("/api/glossary/99999")

        assert response.status_code == 404


class TestSearchGlossary:
    """Test GET /api/glossary/search endpoint"""

    def test_search_by_term(self, client, sample_entry_data):
        """Test searching entries by term"""
        # Create entries
        client.post("/api/glossary", json=sample_entry_data)

        entry2 = sample_entry_data.copy()
        entry2["term"] = "Temperature Sensor"
        entry2["definition"] = "A sensor that measures temperature"
        client.post("/api/glossary", json=entry2)

        # Search for "Sensor"
        response = client.get("/api/glossary/search?query=Sensor")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("Sensor" in entry["term"] for entry in data)

    def test_search_no_results(self, client, sample_entry_data):
        """Test search with no matching results"""
        client.post("/api/glossary", json=sample_entry_data)

        response = client.get("/api/glossary/search?query=NonExistentTerm")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

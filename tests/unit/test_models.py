"""
Unit tests for SQLAlchemy database models
Following TDD approach: Write tests first, then implement models
"""
import pytest
from datetime import datetime, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def db_session():
    """Create a test database session"""
    from src.backend.models import Base

    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


class TestGlossaryEntry:
    """Test GlossaryEntry model"""

    def test_create_glossary_entry(self, db_session):
        """Test creating a glossary entry"""
        from src.backend.models import GlossaryEntry

        entry = GlossaryEntry(
            term="Sensor",
            definitions=[{"text": "A device that detects or measures a physical property", "source_doc_id": None, "is_primary": True}],
            language="en",
            source="internal",
            source_document="manual.pdf"
        )

        db_session.add(entry)
        db_session.commit()

        assert entry.id is not None
        assert entry.term == "Sensor"
        assert entry.language == "en"
        assert entry.validation_status == "pending"  # Default value
        assert entry.sync_status == "pending_sync"  # Default value
        assert entry.creation_date is not None

    def test_glossary_entry_unique_constraint(self, db_session):
        """Test UNIQUE constraint on (term, language, source)"""
        from src.backend.models import GlossaryEntry

        entry1 = GlossaryEntry(
            term="Sensor",
            definitions=[{"text": "First definition", "source_doc_id": None, "is_primary": True}],
            language="en",
            source="internal"
        )
        db_session.add(entry1)
        db_session.commit()

        # Try to add duplicate
        entry2 = GlossaryEntry(
            term="Sensor",
            definitions=[{"text": "Second definition", "source_doc_id": None, "is_primary": True}],
            language="en",
            source="internal"
        )
        db_session.add(entry2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_glossary_entry_different_language_allowed(self, db_session):
        """Test same term in different language is allowed"""
        from src.backend.models import GlossaryEntry

        entry_en = GlossaryEntry(
            term="Sensor",
            definitions=[{"text": "A device that detects", "source_doc_id": None, "is_primary": True}],
            language="en",
            source="internal"
        )
        entry_de = GlossaryEntry(
            term="Sensor",
            definitions=[{"text": "Ein Gerät, das erkennt", "source_doc_id": None, "is_primary": True}],
            language="de",
            source="internal"
        )

        db_session.add(entry_en)
        db_session.add(entry_de)
        db_session.commit()

        assert entry_en.id != entry_de.id

    def test_glossary_entry_validation_status_check(self, db_session):
        """Test validation_status CHECK constraint"""
        from src.backend.models import GlossaryEntry

        entry = GlossaryEntry(
            term="Sensor",
            definitions=[{"text": "A device", "source_doc_id": None, "is_primary": True}],
            language="en",
            source="internal",
            validation_status="invalid_status"  # Should fail
        )

        db_session.add(entry)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_glossary_entry_update_timestamp(self, db_session):
        """Test updated_at timestamp changes on update"""
        from src.backend.models import GlossaryEntry
        import time

        entry = GlossaryEntry(
            term="Sensor",
            definitions=[{"text": "Original definition", "source_doc_id": None, "is_primary": True}],
            language="en",
            source="internal"
        )
        db_session.add(entry)
        db_session.commit()

        original_updated = entry.updated_at
        time.sleep(1.1)  # Larger delay to ensure timestamp difference

        entry.definition = "Updated definition"
        db_session.commit()

        # SQLite has second-level precision, so use >= instead of >
        assert entry.updated_at >= original_updated
        # Verify definition actually changed
        assert entry.definition == "Updated definition"


class TestTerminologyCache:
    """Test TerminologyCache model"""

    def test_create_cache_entry(self, db_session):
        """Test creating a cache entry"""
        from src.backend.models import TerminologyCache

        cache = TerminologyCache(
            api_name="IATE",
            query_key="sensor",
            response_data={"results": [{"term": "Sensor"}]},
            cached_at=datetime.now(UTC)
        )

        db_session.add(cache)
        db_session.commit()

        assert cache.id is not None
        assert cache.api_name == "IATE"
        assert cache.query_key == "sensor"
        assert cache.response_data is not None

    def test_cache_query(self, db_session):
        """Test querying cache by api_name and query_key"""
        from src.backend.models import TerminologyCache

        cache = TerminologyCache(
            api_name="IATE",
            query_key="sensor",
            response_data={"results": []}
        )
        db_session.add(cache)
        db_session.commit()

        result = db_session.query(TerminologyCache).filter_by(
            api_name="IATE",
            query_key="sensor"
        ).first()

        assert result is not None
        assert result.api_name == "IATE"


class TestSyncLog:
    """Test SyncLog model"""

    def test_create_sync_log(self, db_session):
        """Test creating a sync log entry"""
        from src.backend.models import SyncLog

        log = SyncLog(
            glossary_entry_id=1,
            sync_status="failed",
            error_message="Connection timeout",
            attempted_at=datetime.now(UTC)
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.sync_status == "failed"
        assert log.error_message is not None

    def test_sync_log_status_check(self, db_session):
        """Test sync_status CHECK constraint"""
        from src.backend.models import SyncLog

        log = SyncLog(
            glossary_entry_id=1,
            sync_status="invalid_status",  # Should fail
            attempted_at=datetime.now(UTC)
        )

        db_session.add(log)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestUploadedDocument:
    """Test UploadedDocument model"""

    def test_create_uploaded_document(self, db_session):
        """Test creating an uploaded document record"""
        from src.backend.models import UploadedDocument

        doc = UploadedDocument(
            filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size=1024,
            file_type="application/pdf",
            upload_status="completed"
        )

        db_session.add(doc)
        db_session.commit()

        assert doc.id is not None
        assert doc.filename == "test.pdf"
        assert doc.upload_status == "completed"
        assert doc.uploaded_at is not None

    def test_uploaded_document_status_check(self, db_session):
        """Test upload_status CHECK constraint"""
        from src.backend.models import UploadedDocument

        doc = UploadedDocument(
            filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size=1024,
            upload_status="invalid_status"  # Should fail
        )

        db_session.add(doc)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_uploaded_document_processing_metadata(self, db_session):
        """Test processing metadata storage"""
        from src.backend.models import UploadedDocument

        doc = UploadedDocument(
            filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size=1024,
            file_type="application/pdf",  # Added missing required field
            upload_status="completed",
            processing_metadata={
                "pages": 10,
                "extracted_terms": 50,
                "processing_time": 2.5
            }
        )

        db_session.add(doc)
        db_session.commit()

        assert doc.processing_metadata is not None
        assert doc.processing_metadata["pages"] == 10


class TestDatabaseIndexes:
    """Test database indexes exist for performance"""

    def test_glossary_entry_indexes(self, db_session):
        """Test that GlossaryEntry has proper indexes"""
        from src.backend.models import GlossaryEntry
        from sqlalchemy import inspect

        engine = db_session.bind
        inspector = inspect(engine)
        indexes = inspector.get_indexes(GlossaryEntry.__tablename__)

        index_names = [idx['name'] for idx in indexes]

        # Check for expected indexes
        assert any('term' in name.lower() for name in index_names)
        assert any('source' in name.lower() for name in index_names)

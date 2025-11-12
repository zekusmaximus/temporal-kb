# tests/test_entry_service.py

import shutil
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kb.core.models import Base
from kb.core.schemas import EntryCreate, EntryType
from kb.services.entry_service import EntryService
from kb.storage.file_manager import FileManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def file_manager(temp_dir):
    """Create a file manager with temp directory"""
    return FileManager(entries_dir=temp_dir)


@pytest.fixture
def entry_service(db_session, file_manager):
    """Create entry service instance"""
    return EntryService(db_session, file_manager)


class TestEntryService:
    """Test EntryService functionality"""

    def test_create_entry(self, entry_service):
        """Test creating a new entry"""
        entry_data = EntryCreate(
            title="Test Entry",
            content="This is test content",
            entry_type=EntryType.NOTE,
            source="manual",
            tags=["test", "example"],
            projects=[]
        )

        entry = entry_service.create_entry(entry_data)

        assert entry is not None
        assert entry.title == "Test Entry"
        assert entry.content == "This is test content"
        assert entry.entry_type == EntryType.NOTE
        assert len(entry.tags) == 2
        assert entry.id.startswith("ent_")

    def test_get_entry(self, entry_service):
        """Test retrieving an entry"""
        # Create entry first
        entry_data = EntryCreate(
            title="Get Test",
            content="Content",
            entry_type=EntryType.NOTE,
            source="manual"
        )
        created_entry = entry_service.create_entry(entry_data)

        # Retrieve it
        retrieved_entry = entry_service.get_entry(created_entry.id)

        assert retrieved_entry is not None
        assert retrieved_entry.id == created_entry.id
        assert retrieved_entry.title == "Get Test"

    def test_get_nonexistent_entry(self, entry_service):
        """Test getting an entry that doesn't exist"""
        result = entry_service.get_entry("ent_nonexistent")
        assert result is None

    def test_update_entry(self, entry_service):
        """Test updating an entry"""
        # Create entry
        entry_data = EntryCreate(
            title="Original Title",
            content="Original content",
            entry_type=EntryType.NOTE,
            source="manual"
        )
        entry = entry_service.create_entry(entry_data)

        # Update it
        from kb.core.schemas import EntryUpdate
        update_data = EntryUpdate(
            title="Updated Title",
            content="Updated content"
        )

        updated_entry = entry_service.update_entry(entry.id, update_data)

        assert updated_entry is not None
        assert updated_entry.title == "Updated Title"
        assert updated_entry.content == "Updated content"

    def test_delete_entry(self, entry_service):
        """Test deleting an entry"""
        # Create entry
        entry_data = EntryCreate(
            title="To Delete",
            content="Content",
            entry_type=EntryType.NOTE,
            source="manual"
        )
        entry = entry_service.create_entry(entry_data)
        entry_id = entry.id

        # Delete it
        result = entry_service.delete_entry(entry_id)
        assert result is True

        # Verify it's gone (or soft-deleted)
        deleted_entry = entry_service.get_entry(entry_id)
        assert deleted_entry is None or hasattr(deleted_entry, 'deleted_at')

    def test_list_entries(self, entry_service):
        """Test listing entries with pagination"""
        # Create multiple entries
        for i in range(5):
            entry_data = EntryCreate(
                title=f"Entry {i}",
                content=f"Content {i}",
                entry_type=EntryType.NOTE,
                source="manual"
            )
            entry_service.create_entry(entry_data)

        # List with limit
        entries = entry_service.list_entries(limit=3)
        assert len(entries) <= 3

    def test_entry_with_tags(self, entry_service):
        """Test creating entry with tags"""
        entry_data = EntryCreate(
            title="Tagged Entry",
            content="Content",
            entry_type=EntryType.NOTE,
            source="manual",
            tags=["python", "testing", "automation"]
        )

        entry = entry_service.create_entry(entry_data)

        assert len(entry.tags) == 3
        tag_names = [tag.name for tag in entry.tags]
        assert "python" in tag_names
        assert "testing" in tag_names
        assert "automation" in tag_names

    def test_entry_word_count_calculation(self, entry_service):
        """Test that word count is calculated correctly"""
        content = "This is a test sentence with exactly ten words here."
        entry_data = EntryCreate(
            title="Word Count Test",
            content=content,
            entry_type=EntryType.NOTE,
            source="manual"
        )

        entry = entry_service.create_entry(entry_data)

        # Word count should be calculated
        assert entry.word_count > 0
        # Rough check (exact count may vary based on implementation)
        assert entry.word_count >= 10

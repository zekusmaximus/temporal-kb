# tests/test_models.py


import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from kb.core.models import Base, Entry, EntryLink, EntryVersion, Project, Tag
from kb.core.schemas import EntryType


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestEntry:
    """Test Entry model"""

    def test_create_entry(self, db_session):
        """Test creating a basic entry"""
        entry = Entry(
            id="ent_test123",
            title="Test Entry",
            content="Test content",
            entry_type="note",  # Use string instead of enum
            source="manual"
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.id == "ent_test123"
        assert entry.title == "Test Entry"
        assert entry.entry_type == "note"
        assert entry.created_at is not None

    def test_entry_word_count(self, db_session):
        """Test word count calculation"""
        entry = Entry(
            id="ent_test456",
            title="Test",
            content="This is a test with five words.",
            entry_type="note",
            source="manual",
            word_count=7  # "This is a test with five words" = 7 words
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.word_count == 7

    def test_entry_with_tags(self, db_session):
        """Test entry with tags"""
        tag1 = Tag(name="test-tag")
        tag2 = Tag(name="another-tag")

        entry = Entry(
            id="ent_test789",
            title="Tagged Entry",
            content="Content",
            entry_type="note",
            source="manual"
        )
        entry.tags = [tag1, tag2]

        db_session.add(entry)
        db_session.commit()

        assert len(entry.tags) == 2
        assert tag1.name in [t.name for t in entry.tags]

    def test_entry_with_projects(self, db_session):
        """Test entry with projects"""
        project = Project(
            name="test-project",
            description="Test project"
        )

        entry = Entry(
            id="ent_test999",
            title="Project Entry",
            content="Content",
            entry_type="note",
            source="manual"
        )
        entry.projects = [project]

        db_session.add(entry)
        db_session.commit()

        assert len(entry.projects) == 1
        assert entry.projects[0].name == "test-project"


class TestTag:
    """Test Tag model"""

    def test_create_tag(self, db_session):
        """Test creating a tag"""
        tag = Tag(name="test-tag")
        db_session.add(tag)
        db_session.commit()

        assert tag.name == "test-tag"
        assert tag.created_at is not None

    def test_tag_unique_name(self, db_session):
        """Test that tag names must be unique"""
        tag1 = Tag(name="duplicate")
        db_session.add(tag1)
        db_session.commit()

        tag2 = Tag(name="duplicate")
        db_session.add(tag2)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestProject:
    """Test Project model"""

    def test_create_project(self, db_session):
        """Test creating a project"""
        project = Project(
            name="my-project",
            description="A test project"
        )
        db_session.add(project)
        db_session.commit()

        assert project.name == "my-project"
        assert project.description == "A test project"


class TestEntryLink:
    """Test EntryLink model"""

    def test_create_link(self, db_session):
        """Test creating a link between entries"""
        entry1 = Entry(
            id="ent_link1",
            title="Source Entry",
            content="Content",
            entry_type="note",
            source="manual"
        )
        entry2 = Entry(
            id="ent_link2",
            title="Target Entry",
            content="Content",
            entry_type="note",
            source="manual"
        )

        link = EntryLink(
            source_id=entry1.id,
            target_id=entry2.id,
            link_type="references",
            strength=0.85
        )

        db_session.add_all([entry1, entry2, link])
        db_session.commit()

        assert link.source_id == "ent_link1"
        assert link.target_id == "ent_link2"
        assert link.link_type == "references"
        assert link.strength == 0.85


class TestEntryVersion:
    """Test EntryVersion model"""

    def test_create_version(self, db_session):
        """Test creating an entry version"""
        entry = Entry(
            id="ent_version1",
            title="Versioned Entry",
            content="Original content",
            entry_type=EntryType.NOTE,
            source="manual"
        )

        version = EntryVersion(
            entry_id=entry.id,
            version_number=1,
            title="Versioned Entry",
            content="Original content",
            content_hash="abc123"
        )

        db_session.add_all([entry, version])
        db_session.commit()

        assert version.entry_id == entry.id
        assert version.version_number == 1
        assert version.content_hash == "abc123"

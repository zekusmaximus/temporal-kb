# tests/conftest.py

"""
Shared pytest fixtures and configuration for all tests
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kb.core.models import Base


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a session-scoped temporary directory for test data"""
    temp_path = Path(tempfile.mkdtemp(prefix="kb_test_"))
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def clean_db():
    """Create a clean in-memory database for each test"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_entry_data():
    """Sample entry data for testing"""
    return {
        "title": "Test Entry",
        "content": "This is test content with some words in it.",
        "entry_type": "note",
        "source": "manual",
        "tags": ["test", "sample"],
        "projects": [],
    }


# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")

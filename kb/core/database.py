# kb/core/database.py (PostgreSQL version)

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_config
from .models import Base

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, connection_string: str):
        """
        Initialize database with connection string

        Args:
            connection_string: SQLite or PostgreSQL connection string
                SQLite: "sqlite:///path/to/db.db"
                PostgreSQL: "postgresql://user:pass@host:5432/dbname"
        """
        self.connection_string = connection_string

        # Determine if SQLite or PostgreSQL
        self.is_sqlite = connection_string.startswith('sqlite')

        # Create engine with appropriate settings
        if self.is_sqlite:
            self.engine = create_engine(
                connection_string,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            # PostgreSQL
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,  # Verify connections
                pool_size=5,
                max_overflow=10,
                echo=False
            )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()


_db: Optional[Database] = None

def init_db(connection_string: Optional[str | Path] = None) -> Database:
    """Initialize database with given connection string or from config"""
    global _db

    if connection_string is None:
        config = get_config()

        # Check for PostgreSQL config first
        if hasattr(config, 'postgres_url') and config.postgres_url:
            connection_string = config.postgres_url
        else:
            # Fall back to SQLite
            db_path = Path(config.data_dir) / "db" / "kb.db"
            connection_string = f"sqlite:///{db_path}"
    elif isinstance(connection_string, Path):
        # Convert Path to SQLite connection string
        connection_string = f"sqlite:///{connection_string}"

    _db = Database(connection_string)
    _db.create_tables()
    return _db


def get_db() -> Database:
    """Get the global database instance"""
    if _db is None:
        return init_db()
    return _db


def get_session() -> Iterator[Session]:
    """FastAPI dependency: yield a session and ensure close."""
    db = get_db()
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

# kb/services/importers/base.py

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ...core.models import Entry
from ...core.schemas import EntryCreate, EntryType
from ...storage.file_manager import FileManager

logger = logging.getLogger(__name__)


class ImporterBase(ABC):
    """Base class for data importers"""

    def __init__(self, session: Session, file_manager: FileManager):
        self.session = session
        self.file_manager = file_manager
        # Lazy import to avoid circular dependency
        from ..entry_service import EntryService
        self.entry_service = EntryService(session, file_manager)

    @abstractmethod
    def import_data(self, source: Any, **kwargs) -> Dict[str, Any]:
        """
        Import data from source

        Returns:
            Dict with import statistics
        """
        pass

    def create_entry_from_import(
        self,
        title: str,
        content: str,
        entry_type: EntryType,
        source: str,
        source_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        projects: Optional[List[str]] = None
    ) -> Optional[Entry]:
        """Helper method to create entry from imported data"""

        try:
            entry_data = EntryCreate(
                title=title,
                content=content,
                entry_type=entry_type,
                source=source,
                source_metadata=source_metadata,
                tags=tags or [],
                projects=projects or []
            )

            return self.entry_service.create_entry(entry_data)

        except Exception as e:
            logger.error(f"Failed to create entry from import: {e}")
            return None

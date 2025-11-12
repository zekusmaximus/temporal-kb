# kb/services/import_service.py

import logging
from typing import Optional

from sqlalchemy.orm import Session

from ..storage.file_manager import FileManager
from .importers.base import ImporterBase
from .importers.browser_importer import BrowserHistoryImporter
from .importers.chat_importer import ChatExportImporter
from .importers.email_importer import EmailImporter
from .importers.markdown_importer import MarkdownImporter

logger = logging.getLogger(__name__)


class ImportService:
    """Main import service coordinating all importers"""

    def __init__(self, session: Session, file_manager: FileManager):
        self.session = session
        self.file_manager = file_manager

    def get_importer(self, importer_type: str) -> Optional[ImporterBase]:
        """Get specific importer by type"""

        # Only include importers that are implemented
        importers = {
            'email': EmailImporter,
            'markdown': MarkdownImporter,
            'browser': BrowserHistoryImporter,
            'chat': ChatExportImporter,
        }

        importer_class = importers.get(importer_type)
        if importer_class:
            return importer_class(self.session, self.file_manager)

        return None

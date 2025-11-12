# kb/services/importers/browser_importer.py

import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ...core.schemas import EntryType
from .base import ImporterBase

logger = logging.getLogger(__name__)


class BrowserHistoryImporter(ImporterBase):
    """Import browser history and bookmarks"""

    BROWSER_PATHS = {
        "chrome": {
            "darwin": Path.home() / "Library/Application Support/Google/Chrome/Default/History",
            "linux": Path.home() / ".config/google-chrome/Default/History",
            "win32": Path.home() / "AppData/Local/Google/Chrome/User Data/Default/History",
        },
        "firefox": {
            "darwin": Path.home() / "Library/Application Support/Firefox/Profiles",
            "linux": Path.home() / ".mozilla/firefox",
            "win32": Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles",
        },
        "safari": {"darwin": Path.home() / "Library/Safari/History.db"},
    }

    def import_data(
        self,
        source: str,
        browser: str = "chrome",
        since_date: Optional[datetime] = None,
        url_filter: Optional[str] = None,
        min_visit_duration: int = 30,  # seconds
        limit: int = 500,
    ) -> Dict[str, Any]:
        """
        Import browser history

        Args:
            source: Browser database path (or 'auto' for auto-detection)
            browser: Browser type ('chrome', 'firefox', 'safari')
            since_date: Only import visits after this date
            url_filter: SQL LIKE pattern for URLs
            min_visit_duration: Minimum time on page (seconds)
            limit: Maximum entries to import

        Returns:
            Import statistics
        """

        stats = {"visits_found": 0, "visits_imported": 0, "visits_skipped": 0, "errors": []}

        try:
            # Get browser database path
            if source == "auto":
                import sys

                platform = sys.platform
                db_path = self.BROWSER_PATHS.get(browser, {}).get(platform)

                if not db_path or not db_path.exists():
                    raise ValueError(f"Could not find {browser} database")
            else:
                db_path = Path(source)

            # Copy database (browser may have it locked)
            import tempfile

            temp_db = Path(tempfile.mktemp(suffix=".db"))
            shutil.copy(db_path, temp_db)

            # Connect to database
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()

            # Build query based on browser
            if browser == "chrome":
                query = self._build_chrome_query(since_date, url_filter, limit)
            elif browser == "firefox":
                query = self._build_firefox_query(since_date, url_filter, limit)
            elif browser == "safari":
                query = self._build_safari_query(since_date, url_filter, limit)
            else:
                raise ValueError(f"Unsupported browser: {browser}")

            cursor.execute(query)
            results = cursor.fetchall()
            stats["visits_found"] = len(results)

            # Process results
            for row in results:
                try:
                    url, title, visit_time, visit_count = row[:4]

                    # Skip if no title
                    if not title or title.strip() == "":
                        stats["visits_skipped"] += 1
                        continue

                    # Create entry
                    entry_title = f"Browsed: {title}"
                    content = f"**URL:** {url}\n\n**Visited:** {visit_time}\n**Visit Count:** {visit_count}"

                    source_metadata = {
                        "url": url,
                        "visit_time": visit_time,
                        "visit_count": visit_count,
                        "browser": browser,
                    }

                    tags = ["browsing", "imported", browser]

                    # Extract domain for tagging
                    from urllib.parse import urlparse

                    domain = urlparse(url).netloc
                    if domain:
                        tags.append(f"site-{domain.replace('www.', '')}")

                    entry = self.create_entry_from_import(
                        title=entry_title,
                        content=content,
                        entry_type=EntryType.WEB_CLIP,
                        source="browser_history",
                        source_metadata=source_metadata,
                        tags=tags,
                    )

                    if entry:
                        stats["visits_imported"] += 1
                    else:
                        stats["visits_skipped"] += 1

                except Exception as e:
                    stats["visits_skipped"] += 1
                    stats["errors"].append(f"Visit {url}: {str(e)}")

            # Cleanup
            conn.close()
            temp_db.unlink()

        except Exception as e:
            stats["errors"].append(f"Browser import failed: {str(e)}")
            logger.error(f"Browser import failed: {e}")

        return stats

    def _build_chrome_query(
        self, since_date: Optional[datetime], url_filter: Optional[str], limit: int
    ) -> str:
        """Build Chrome history query"""

        query = """
            SELECT url, title, datetime(last_visit_time/1000000-11644473600, 'unixepoch'), visit_count
            FROM urls
            WHERE title IS NOT NULL AND title != ''
        """

        if since_date:
            # Chrome uses webkit timestamp
            webkit_time = int((since_date.timestamp() + 11644473600) * 1000000)
            query += f" AND last_visit_time > {webkit_time}"

        if url_filter:
            query += f" AND url LIKE '%{url_filter}%'"

        query += f" ORDER BY last_visit_time DESC LIMIT {limit}"

        return query

    def _build_firefox_query(
        self, since_date: Optional[datetime], url_filter: Optional[str], limit: int
    ) -> str:
        """Build Firefox history query"""

        query = """
            SELECT url, title, datetime(last_visit_date/1000000, 'unixepoch'), visit_count
            FROM moz_places
            WHERE title IS NOT NULL AND title != ''
        """

        if since_date:
            timestamp = int(since_date.timestamp() * 1000000)
            query += f" AND last_visit_date > {timestamp}"

        if url_filter:
            query += f" AND url LIKE '%{url_filter}%'"

        query += f" ORDER BY last_visit_date DESC LIMIT {limit}"

        return query

    def _build_safari_query(
        self, since_date: Optional[datetime], url_filter: Optional[str], limit: int
    ) -> str:
        """Build Safari history query"""

        query = """
            SELECT url, title, datetime(visit_time + 978307200, 'unixepoch'), visit_count
            FROM history_items
            JOIN history_visits ON history_items.id = history_visits.history_item
            WHERE title IS NOT NULL AND title != ''
        """

        if since_date:
            # Safari uses Mac absolute time
            mac_time = since_date.timestamp() - 978307200
            query += f" AND visit_time > {mac_time}"

        if url_filter:
            query += f" AND url LIKE '%{url_filter}%'"

        query += f" ORDER BY visit_time DESC LIMIT {limit}"

        return query

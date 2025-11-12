# kb/storage/file_manager.py

import re
from pathlib import Path
from typing import Optional

import yaml

from ..core.config import get_config
from ..core.models import Entry


class FileManager:
    def __init__(self, entries_dir: Optional[Path] = None):
        config = get_config()
        self.entries_dir = entries_dir or config.entries_dir
        self.entries_dir.mkdir(parents=True, exist_ok=True)

    def save_entry(self, entry: Entry) -> Path:
        """Save entry to markdown file with YAML frontmatter"""

        # Determine subdirectory based on entry type
        subdir = self.entries_dir / entry.entry_type
        subdir.mkdir(exist_ok=True)

        # Generate filename from title (sanitized)
        filename = self._sanitize_filename(entry.title) + ".md"
        filepath = subdir / filename

        # Handle filename conflicts
        counter = 1
        while filepath.exists():
            stem = self._sanitize_filename(entry.title)
            filename = f"{stem}_{counter}.md"
            filepath = subdir / filename
            counter += 1

        # Prepare YAML frontmatter
        frontmatter = {
            "id": entry.id,
            "title": entry.title,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "entry_type": entry.entry_type,
            "tags": [tag.name for tag in entry.tags],
            "projects": [project.name for project in entry.projects],
            "word_count": entry.word_count,
            "is_public": entry.is_public,
        }

        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True)
            f.write("---\n\n")
            f.write(entry.content)

        return filepath

    def delete_entry(self, entry: Entry):
        """Delete entry file"""
        if entry.file_path:
            filepath = self.entries_dir / entry.file_path
            if filepath.exists():
                filepath.unlink()

    def read_entry_file(self, filepath: Path) -> tuple[dict, str]:
        """Read markdown file and extract frontmatter + content"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse frontmatter
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, content, re.DOTALL)

        if match:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2).strip()
            return frontmatter, body
        else:
            return {}, content

    def _sanitize_filename(self, title: str) -> str:
        """Convert title to safe filename"""
        # Remove invalid characters
        safe = re.sub(r'[<>:"/\\|?*]', "", title)
        # Replace spaces and special chars with underscores
        safe = re.sub(r"\s+", "_", safe)
        # Limit length
        return safe[:100].lower()

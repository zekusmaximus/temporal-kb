# kb/services/entry_service.py

import hashlib
from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..core.models import Entry, EntryProject, EntryTag, EntryVersion, Project, Tag
from ..core.schemas import EntryCreate, EntryUpdate
from ..storage.file_manager import FileManager
from ..utils.text_processing import calculate_word_count


class EntryService:
    def __init__(self, session: Session, file_manager: FileManager):
        self.session = session
        self.file_manager = file_manager

    def create_entry(self, entry_data: EntryCreate) -> Entry:
        """Create a new entry with version tracking"""

        # Calculate content hash
        content_hash = hashlib.sha256(entry_data.content.encode()).hexdigest()

        # Create entry object
        entry = Entry(
            entry_type=entry_data.entry_type.value,
            title=entry_data.title,
            content=entry_data.content,
            content_hash=content_hash,
            source=entry_data.source,
            source_metadata=entry_data.source_metadata,
            vault_id=entry_data.vault_id,
            is_public=entry_data.is_public,
            word_count=calculate_word_count(entry_data.content)
        )

        self.session.add(entry)
        self.session.flush()  # Get entry.id without committing

        # Create initial version
        version = EntryVersion(
            entry_id=entry.id,
            version_number=1,
            content=entry_data.content,
            content_hash=content_hash,
            change_type="create",
            change_summary="Initial creation"
        )
        self.session.add(version)

        # Handle tags
        if entry_data.tags:
            self._add_tags(entry, entry_data.tags)

        # Handle projects
        if entry_data.projects:
            self._add_projects(entry, entry_data.projects)

        # Save to file system
        file_path = self.file_manager.save_entry(entry)
        entry.file_path = str(file_path.relative_to(self.file_manager.entries_dir))

        self.session.commit()
        self.session.refresh(entry)

        return entry

    def get_entry(self, entry_id: str) -> Optional[Entry]:
        """Retrieve an entry by ID"""
        return self.session.query(Entry).filter(Entry.id == entry_id).first()

    def update_entry(self, entry_id: str, update_data: EntryUpdate) -> Entry:
        """Update an entry and create a new version"""
        entry = self.get_entry(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")

        # Track what changed
        changes = []

        if update_data.title and update_data.title != entry.title:
            entry.title = update_data.title
            changes.append("title")

        if update_data.content and update_data.content != entry.content:
            # Create new version
            new_hash = hashlib.sha256(update_data.content.encode()).hexdigest()
            if new_hash != entry.content_hash:
                # Get latest version number
                latest_version = self.session.query(EntryVersion)\
                    .filter(EntryVersion.entry_id == entry_id)\
                    .order_by(desc(EntryVersion.version_number))\
                    .first()

                new_version_num = (latest_version.version_number + 1) if latest_version else 1

                # Create version record
                version = EntryVersion(
                    entry_id=entry_id,
                    version_number=new_version_num,
                    content=update_data.content,
                    content_hash=new_hash,
                    change_type="edit",
                    change_summary=f"Updated: {', '.join(changes)}" if changes else "Content update"
                )
                self.session.add(version)

                # Update entry
                entry.content = update_data.content
                entry.content_hash = new_hash
                entry.word_count = calculate_word_count(update_data.content)
                entry.updated_at = datetime.utcnow()
                changes.append("content")

        if update_data.tags is not None:
            self._update_tags(entry, update_data.tags)
            changes.append("tags")

        if update_data.projects is not None:
            self._update_projects(entry, update_data.projects)
            changes.append("projects")

        if update_data.is_public is not None:
            entry.is_public = update_data.is_public

        # Update file system
        if changes:
            self.file_manager.save_entry(entry)

        self.session.commit()
        self.session.refresh(entry)

        return entry

    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry and its file"""
        entry = self.get_entry(entry_id)
        if not entry:
            return False

        # Delete file
        if entry.file_path:
            self.file_manager.delete_entry(entry)

        # Delete from database (cascade handles versions, links, etc.)
        self.session.delete(entry)
        self.session.commit()

        return True

    def get_entry_versions(self, entry_id: str) -> List[EntryVersion]:
        """Get all versions of an entry"""
        return self.session.query(EntryVersion)\
            .filter(EntryVersion.entry_id == entry_id)\
            .order_by(desc(EntryVersion.version_number))\
            .all()

    def get_version_content(self, entry_id: str, version_number: int) -> Optional[str]:
        """Get content from a specific version"""
        version = self.session.query(EntryVersion)\
            .filter(
                EntryVersion.entry_id == entry_id,
                EntryVersion.version_number == version_number
            )\
            .first()

        return version.content if version else None

    def _add_tags(self, entry: Entry, tag_names: List[str]):
        """Add tags to an entry"""
        for tag_name in tag_names:
            tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                self.session.add(tag)
                self.session.flush()

            entry_tag = EntryTag(entry_id=entry.id, tag_id=tag.id)
            self.session.add(entry_tag)

    def _update_tags(self, entry: Entry, tag_names: List[str]):
        """Update entry tags (replace all)"""
        # Remove existing tags
        self.session.query(EntryTag).filter(EntryTag.entry_id == entry.id).delete()
        # Add new tags
        self._add_tags(entry, tag_names)

    def _add_projects(self, entry: Entry, project_names: List[str]):
        """Add projects to an entry"""
        for project_name in project_names:
            project = self.session.query(Project).filter(Project.name == project_name).first()
            if not project:
                # Auto-create project if it doesn't exist
                project = Project(name=project_name, project_type="unknown", status="active")
                self.session.add(project)
                self.session.flush()

            entry_project = EntryProject(entry_id=entry.id, project_id=project.id)
            self.session.add(entry_project)

    def _update_projects(self, entry: Entry, project_names: List[str]):
        """Update entry projects (replace all)"""
        # Remove existing projects
        self.session.query(EntryProject).filter(EntryProject.entry_id == entry.id).delete()
        # Add new projects
        self._add_projects(entry, project_names)

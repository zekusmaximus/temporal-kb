# kb/services/importers/markdown_importer.py

from pathlib import Path
from typing import Dict, Any, List
import re
import yaml
from datetime import datetime
import logging

from .base import ImporterBase
from ...core.schemas import EntryType
from ...utils.text_processing import extract_yaml_frontmatter
 
logger = logging.getLogger(__name__)

class MarkdownImporter(ImporterBase):
    """Import markdown files from directories"""
    
    def import_data(
        self,
        source: Path,
        recursive: bool = True,
        tags: List[str] = None,
        project: str = None
    ) -> Dict[str, Any]:
        """
        Import markdown files from a directory
        
        Args:
            source: Directory path
            recursive: Scan subdirectories
            tags: Tags to add to all imported entries
            project: Project to associate with imports
        
        Returns:
            Import statistics
        """
        
        source_path = Path(source)
        if not source_path.exists():
            raise ValueError(f"Source path does not exist: {source}")
        
        stats = {
            'files_found': 0,
            'files_imported': 0,
            'files_skipped': 0,
            'errors': []
        }
        
        # Find markdown files
        pattern = "**/*.md" if recursive else "*.md"
        md_files = list(source_path.glob(pattern))
        stats['files_found'] = len(md_files)
        
        for md_file in md_files:
            try:
                # Read file
                content = md_file.read_text(encoding='utf-8')
                
                # Extract frontmatter if present
                frontmatter, body = extract_yaml_frontmatter(content)
                
                # Determine title
                title = frontmatter.get('title') if frontmatter else None
                if not title:
                    # Use first heading or filename
                    heading_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
                    if heading_match:
                        title = heading_match.group(1).strip()
                    else:
                        title = md_file.stem
                
                # Combine tags
                file_tags = frontmatter.get('tags', []) if frontmatter else []
                if tags:
                    file_tags.extend(tags)
                if not file_tags:
                    file_tags = ['imported', 'markdown']
                
                # Determine projects
                projects = []
                if project:
                    projects.append(project)
                if frontmatter and 'project' in frontmatter:
                    projects.append(frontmatter['project'])
                
                # Determine entry type
                entry_type = EntryType.NOTE
                if frontmatter and 'type' in frontmatter:
                    try:
                        entry_type = EntryType(frontmatter['type'])
                    except ValueError:
                        pass
                
                # Create entry
                source_metadata = {
                    'original_path': str(md_file),
                    'imported_at': datetime.utcnow().isoformat(),
                    'file_size': md_file.stat().st_size,
                    'file_modified': datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                }
                
                entry = self.create_entry_from_import(
                    title=title,
                    content=body,
                    entry_type=entry_type,
                    source='markdown_import',
                    source_metadata=source_metadata,
                    tags=file_tags,
                    projects=projects
                )
                
                if entry:
                    stats['files_imported'] += 1
                else:
                    stats['files_skipped'] += 1
            
            except Exception as e:
                stats['files_skipped'] += 1
                stats['errors'].append(f"{md_file.name}: {str(e)}")
                logger.error(f"Failed to import {md_file}: {e}")
        
        return stats

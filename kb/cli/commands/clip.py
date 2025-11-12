# kb/cli/commands/clip.py

import click
import pyperclip
from datetime import datetime

from ...core.database import get_db
from ...core.schemas import EntryCreate, EntryType
from ...services.entry_service import EntryService
from ...storage.file_manager import FileManager
from ..ui import print_success, print_error, prompt_text

@click.command()
@click.option('--title', '-t', help='Clip title')
@click.option('--tags', '-T', multiple=True, help='Tags')
@click.option('--url', '-u', help='Source URL')
def clip(title, tags, url):
    """Save clipboard content as an entry
    
    Examples:
        kb clip  # Saves clipboard with auto-title
        kb clip -t "Interesting Article" -u https://example.com
    """
    
    try:
        # Get clipboard content
        content = pyperclip.paste()
        if not content or not content.strip():
            print_error("Clipboard is empty")
            return
        
        # Auto-generate title if not provided
        if not title:
            # Use first line or timestamp
            first_line = content.split('\n')[0][:50]
            if first_line:
                title = f"Clip: {first_line}"
            else:
                title = f"Clip - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Prepare metadata
        source_metadata = {}
        if url:
            source_metadata['url'] = url
            content = f"Source: {url}\n\n---\n\n{content}"
        
        # Save entry
        db = get_db()
        with db.session_scope() as session:
            file_manager = FileManager()
            entry_service = EntryService(session, file_manager)
            
            entry_data = EntryCreate(
                title=title,
                content=content,
                entry_type=EntryType.WEB_CLIP,
                tags=list(tags) if tags else ['clip'],
                source='clipboard',
                source_metadata=source_metadata if source_metadata else None
            )
            
            entry = entry_service.create_entry(entry_data)
        
        print_success(f"✓ Clip saved: {entry.id}")
        print_success(f"  {entry.title}")
    
    except Exception as e:
        print_error(f"Failed to save clip: {str(e)}")
        raise
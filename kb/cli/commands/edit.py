# kb/cli/commands/edit.py

import click
from ...core.database import get_db
from ...core.schemas import EntryUpdate
from ...services.entry_service import EntryService
from ...storage.file_manager import FileManager
from ..ui import (
    console, print_success, print_error, print_entry,
    prompt_for_editor, prompt_text, confirm_action
)

@click.command()
@click.argument('entry_id')
@click.option('--title', '-t', help='New title')
@click.option('--content', '-c', help='New content')
@click.option('--editor', '-e', is_flag=True, help='Open editor')
@click.option('--add-tag', 'add_tags', multiple=True, help='Add tags')
@click.option('--remove-tag', 'remove_tags', multiple=True, help='Remove tags')
@click.option('--add-project', 'add_projects', multiple=True, help='Add projects')
@click.option('--remove-project', 'remove_projects', multiple=True, help='Remove projects')
def edit(entry_id, title, content, editor, add_tags, remove_tags, add_projects, remove_projects):
    """Edit an existing entry
    
    Examples:
        kb edit ent_a1b2c3d4e5f6 --editor
        kb edit ent_a1b2c3d4e5f6 --title "New Title"
        kb edit ent_a1b2c3d4e5f6 --add-tag philosophy
    """
    
    db = get_db()
    
    try:
        with db.session_scope() as session:
            file_manager = FileManager()
            entry_service = EntryService(session, file_manager)
            
            # Get current entry
            entry = entry_service.get_entry(entry_id)
            if not entry:
                print_error(f"Entry not found: {entry_id}")
                return
            
            # Show current entry
            print_entry(entry, show_content=False)
            console.print()
            
            # Prepare update
            update_data = EntryUpdate()
            
            if title:
                update_data.title = title
            
            if editor:
                with console.status("[bold blue]Opening editor..."):
                    new_content = prompt_for_editor(entry.content)
                if new_content != entry.content:
                    update_data.content = new_content
            elif content:
                update_data.content = content
            
            # Handle tags
            if add_tags or remove_tags:
                current_tags = {tag.name for tag in entry.tags}
                current_tags.update(add_tags)
                current_tags.difference_update(remove_tags)
                update_data.tags = list(current_tags)
            
            # Handle projects
            if add_projects or remove_projects:
                current_projects = {proj.name for proj in entry.projects}
                current_projects.update(add_projects)
                current_projects.difference_update(remove_projects)
                update_data.projects = list(current_projects)
            
            # Apply update
            if any([update_data.title, update_data.content, 
                    update_data.tags is not None, update_data.projects is not None]):
                
                if confirm_action("Save changes?", default=True):
                    updated_entry = entry_service.update_entry(entry_id, update_data)
                    print_success("✓ Entry updated")
                    print_entry(updated_entry, show_content=False)
                    
                    # Git commit
                    from .add import _git_commit
                    _git_commit(updated_entry, "update")
                else:
                    print_warning("Changes discarded")
            else:
                print_warning("No changes made")
    
    except Exception as e:
        print_error(f"Failed to edit entry: {str(e)}")
        raise
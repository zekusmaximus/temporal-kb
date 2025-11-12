# kb/cli/commands/delete.py

import click

from ...core.database import get_db
from ...services.entry_service import EntryService
from ...storage.file_manager import FileManager
from ..ui import confirm_action, console, print_entry, print_error, print_success, print_warning


@click.command()
@click.argument("entry_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete(entry_id, force):
    """Delete an entry

    Examples:
        kb delete ent_a1b2c3d4e5f6
        kb delete ent_a1b2c3d4e5f6 --force
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            file_manager = FileManager()
            entry_service = EntryService(session, file_manager)

            # Get entry
            entry = entry_service.get_entry(entry_id)
            if not entry:
                print_error(f"Entry not found: {entry_id}")
                return

            # Show entry
            print_entry(entry, show_content=False)

            # Confirm deletion
            if not force:
                if not confirm_action(
                    f"[bold red]Delete '{entry.title}'?[/bold red]\n"
                    f"This will delete {len(entry.versions)} versions and cannot be undone.",
                    default=False,
                ):
                    print_warning("Deletion cancelled")
                    return

            # Delete
            with console.status("[bold red]Deleting entry..."):
                entry_service.delete_entry(entry_id)

            print_success(f"✓ Entry deleted: {entry.title}")

            # Git commit
            from ...core.config import get_config

            config = get_config()
            if config.git_enabled and config.git_auto_commit:
                from ...storage.git_manager import GitManager

                git_mgr = GitManager(config.data_dir)
                git_mgr.commit(f"Delete: {entry.title}")

    except Exception as e:
        print_error(f"Failed to delete entry: {str(e)}")
        raise

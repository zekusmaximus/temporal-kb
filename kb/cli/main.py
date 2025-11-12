# kb/cli/main.py

import click
from pathlib import Path
from typing import Optional
import sys

from ..core.database import init_db, get_db
from ..core.config import init_config, get_config
from ..storage.file_manager import FileManager
from ..services.entry_service import EntryService
from .ui import console, print_entry, print_entries_table, print_success, print_error, print_warning


@click.group()
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
@click.option("--data-dir", type=click.Path(), help="Override data directory")
@click.pass_context
def cli(ctx, config, data_dir):
    """Temporal Knowledge Base - Your personal wiki with memory"""

    # Initialize configuration
    if config:
        init_config(Path(config))
    else:
        init_config()

    cfg = get_config()

    # Override data directory if provided
    if data_dir:
        cfg.data_dir = Path(data_dir)
        cfg.db_path = cfg.data_dir / "db" / "kb.db"
        cfg.entries_dir = cfg.data_dir / "entries"

    # Initialize database
    init_db(cfg.db_path)

    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg
    ctx.obj["db"] = get_db()


@cli.command()
def init():
    """Initialize a new knowledge base"""
    config = get_config()

    with console.status("[bold blue]Initializing knowledge base..."):
        # Create directories
        config.data_dir.mkdir(parents=True, exist_ok=True)
        config.entries_dir.mkdir(parents=True, exist_ok=True)
        config.vector_db_path.mkdir(parents=True, exist_ok=True)

        # Initialize database
        db = get_db()
        db.create_tables()

        # Initialize git repo if enabled
        if config.git_enabled:
            from ..storage.git_manager import GitManager

            git_mgr = GitManager(config.data_dir)
            git_mgr.init_repo()

    print_success(f"✓ Knowledge base initialized at {config.data_dir}")
    print(f"\nNext steps:")
    print(f"  kb add        - Create your first entry")
    print(f"  kb search     - Search your knowledge base")
    print(f"  kb import     - Import existing data")


@cli.command()
def info():
    """Show knowledge base information"""
    config = get_config()
    db = get_db()

    with db.session_scope() as session:
        from ..core.models import Entry, Tag, Project, EntryLink

        entry_count = session.query(Entry).count()
        tag_count = session.query(Tag).count()
        project_count = session.query(Project).count()
        link_count = session.query(EntryLink).count()

    from rich.table import Table

    table = Table(title="Knowledge Base Info", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Data Directory", str(config.data_dir))
    table.add_row("Database", str(config.db_path))
    table.add_row("Entries", str(entry_count))
    table.add_row("Tags", str(tag_count))
    table.add_row("Projects", str(project_count))
    table.add_row("Links", str(link_count))
    table.add_row("Git Enabled", "✓" if config.git_enabled else "✗")
    table.add_row("Encryption", "✓" if config.encryption_enabled else "✗")

    console.print(table)


# Import subcommand modules (only ones that exist)
from .commands import (
    add,
    search,
    edit,
    delete,
    link,
    temporal,
    serve,
    show,
    import_cmd,
    clip,
    index,
)

# Register commands
cli.add_command(add.add)
cli.add_command(search.search)
cli.add_command(edit.edit)
cli.add_command(delete.delete)
cli.add_command(link.link)
cli.add_command(temporal.temporal)
cli.add_command(serve.serve)
cli.add_command(show.show)
cli.add_command(import_cmd.import_data)
cli.add_command(clip.clip)
cli.add_command(index.index)


def main():
    """Entry point for the CLI"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        print_warning("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

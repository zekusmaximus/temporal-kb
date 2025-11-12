# kb/cli/commands/index.py

import click

from ...core.config import get_config
from ...core.database import get_db
from ...core.models import Entry
from ...storage.vector_store import VectorStore
from ..ui import confirm_action, console, print_error, print_info, print_success, print_warning


@click.group()
def index():
    """Manage search indexes"""
    pass

@index.command()
@click.option('--force', '-f', is_flag=True, help='Force rebuild without confirmation')
def rebuild(force):
    """Rebuild vector search index

    This will re-generate embeddings for all entries.
    Useful after changing embedding models or fixing corruption.
    """

    config = get_config()
    db = get_db()

    if not force:
        if not confirm_action(
            "[yellow]Rebuild entire vector index?[/yellow]\n"
            "This may take several minutes for large knowledge bases.",
            default=False
        ):
            print_warning("Index rebuild cancelled")
            return

    try:
        with console.status("[bold blue]Rebuilding vector index..."):
            with db.session_scope() as session:
                # Get all entries
                entries = session.query(Entry).all()
                print_info(f"Found {len(entries)} entries to index")

                # Rebuild index
                vector_store = VectorStore(config.vector_db_path, model_name=config.embedding_model)
                count = vector_store.rebuild_index(entries)

        print_success(f"✓ Vector index rebuilt with {count} entries")

    except Exception as e:
        print_error(f"Failed to rebuild index: {str(e)}")
        raise

@index.command()
def stats():
    """Show index statistics"""

    config = get_config()
    db = get_db()

    try:
        # Database stats
        with db.session_scope() as session:
            from ...services.search_service import SearchService
            search_service = SearchService(session)

            total_entries = session.query(Entry).count()
            popular_tags = search_service.get_popular_tags(limit=10)
            orphaned = len(search_service.get_orphaned_entries())

        # Vector store stats
        if config.semantic_search_enabled:
            vector_store = VectorStore(config.vector_db_path)
            vector_stats = vector_store.get_stats()
        else:
            vector_stats = None

        # Display stats
        from rich.table import Table

        table = Table(title="Search Index Statistics", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Entries", str(total_entries))
        table.add_row("Orphaned Entries", str(orphaned))

        if vector_stats:
            table.add_row("Vector Index Entries", str(vector_stats['entry_count']))
            table.add_row("Embedding Model", vector_stats['model_name'])
        else:
            table.add_row("Vector Index", "[red]Disabled[/red]")

        console.print(table)

        # Show popular tags
        if popular_tags:
            console.print("\n[bold cyan]Popular Tags:[/bold cyan]")
            for tag in popular_tags:
                console.print(f"  #{tag['name']}: {tag['count']} entries")

    except Exception as e:
        print_error(f"Failed to get stats: {str(e)}")
        raise

@index.command()
@click.option('--entry-id', help='Index specific entry')
@click.option('--all', 'index_all', is_flag=True, help='Index all entries')
def update(entry_id, index_all):
    """Update vector index for specific entries"""

    config = get_config()
    db = get_db()

    if not config.semantic_search_enabled:
        print_error("Semantic search is not enabled")
        return

    try:
        vector_store = VectorStore(config.vector_db_path)

        with db.session_scope() as session:
            if entry_id:
                # Index single entry
                entry = session.query(Entry).filter(Entry.id == entry_id).first()
                if not entry:
                    print_error(f"Entry not found: {entry_id}")
                    return

                with console.status("[bold blue]Updating index..."):
                    vector_store.add_entry(entry)

                print_success(f"✓ Indexed entry: {entry.title}")

            elif index_all:
                # Index all entries
                entries = session.query(Entry).all()

                with console.status(f"[bold blue]Indexing {len(entries)} entries..."):
                    count = vector_store.add_entries_batch(entries)

                print_success(f"✓ Indexed {count} entries")

            else:
                print_error("Specify --entry-id or --all")

    except Exception as e:
        print_error(f"Failed to update index: {str(e)}")
        raise

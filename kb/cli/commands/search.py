# kb/cli/commands/search.py


import click

from ...core.config import get_config
from ...core.database import get_db
from ...core.models import Entry
from ...core.schemas import EntryType
from ...services.search_service import SearchService
from ..ui import (
    confirm_action,
    console,
    print_entries_table,
    print_entry,
    print_error,
    print_success,
    print_warning,
)

# kb/cli/commands/search.py (enhanced)

@click.command()
@click.argument('query', required=False)
@click.option('--semantic', '-s', is_flag=True, help='Use semantic search')
@click.option('--hybrid', is_flag=True, help='Use hybrid search (semantic + keyword)')
@click.option('--similar-to', help='Find entries similar to this entry ID')
@click.option('--type', 'entry_types', multiple=True,
              type=click.Choice([t.value for t in EntryType]),
              help='Filter by entry type')
@click.option('--tag', '-t', 'tags', multiple=True, help='Filter by tags')
@click.option('--project', '-p', 'projects', multiple=True, help='Filter by projects')
@click.option('--from', 'date_from', help='From date (YYYY-MM-DD)')
@click.option('--to', 'date_to', help='To date (YYYY-MM-DD)')
@click.option('--limit', '-n', default=50, help='Max results')
@click.option('--show-content', '-c', is_flag=True, help='Show full content')
@click.option('--show-scores', is_flag=True, help='Show relevance scores')
@click.option('--recent', '-r', type=int, help='Show N most recent entries')
@click.option('--today', is_flag=True, help='Show entries from today')
@click.option('--orphaned', is_flag=True, help='Find orphaned entries (no tags/links)')
def search(query, semantic, hybrid, similar_to, entry_types, tags, projects,
           date_from, date_to, limit, show_content, show_scores, recent,
           today, orphaned):
    """Search your knowledge base with multiple search modes

    Examples:
        # Keyword search
        kb search "digital consciousness"

        # Semantic search
        kb search "Buddhist concepts in cyberpunk" --semantic

        # Hybrid search (best of both)
        kb search "narrative structures" --hybrid

        # Find similar entries
        kb search --similar-to ent_a1b2c3d4e5f6

        # Recent entries
        kb search --recent 10

        # Find orphaned entries
        kb search --orphaned
    """

    db = get_db()
    config = get_config()

    try:
        with db.session_scope() as session:
            search_service = SearchService(session)

            # Handle orphaned entries
            if orphaned:
                entries = search_service.get_orphaned_entries()
                if entries:
                    print_entries_table(entries, show_preview=True)
                    console.print(f"\n[yellow]Found {len(entries)} orphaned entries[/yellow]")
                    console.print("[dim]Consider adding tags or linking these entries[/dim]")
                else:
                    print_success("No orphaned entries found")
                return

            # Handle similar-to search
            if similar_to:
                if not config.semantic_search_enabled:
                    print_error("Semantic search is not enabled")
                    return

                from ...storage.vector_store import VectorStore
                vector_store = VectorStore(config.vector_db_path)

                with console.status("[bold blue]Finding similar entries..."):
                    results = vector_store.find_similar(similar_to, limit=limit)

                if results:
                    # Get full entries
                    entry_ids = [r['id'] for r in results]
                    entries = session.query(Entry).filter(Entry.id.in_(entry_ids)).all()
                    entries_dict = {e.id: e for e in entries}
                    sorted_entries = [entries_dict[r['id']] for r in results if r['id'] in entries_dict]

                    print_entries_table(sorted_entries, show_preview=True)

                    if show_scores:
                        console.print("\n[bold cyan]Similarity Scores:[/bold cyan]")
                        for r in results:
                            console.print(f"  {r['id'][:12]}: {r['similarity']:.3f}")
                else:
                    print_warning("No similar entries found")
                return

            # Handle semantic search
            if semantic:
                if not query:
                    print_error("Query required for semantic search")
                    return

                if not config.semantic_search_enabled:
                    print_error("Semantic search is not enabled")
                    return

                from ...storage.vector_store import VectorStore
                vector_store = VectorStore(config.vector_db_path)

                with console.status("[bold blue]Performing semantic search..."):
                    results = vector_store.search(query, limit=limit)

                if results:
                    entry_ids = [r['id'] for r in results]
                    entries = session.query(Entry).filter(Entry.id.in_(entry_ids)).all()
                    entries_dict = {e.id: e for e in entries}
                    sorted_entries = [entries_dict[r['id']] for r in results if r['id'] in entries_dict]

                    print_entries_table(sorted_entries, show_preview=True)

                    if show_scores:
                        console.print("\n[bold cyan]Relevance Scores:[/bold cyan]")
                        for r in results:
                            console.print(f"  {r['id'][:12]}: {r['similarity']:.3f}")
                else:
                    print_warning("No semantically similar entries found")

            # Handle hybrid search
            elif hybrid:
                if not query:
                    print_error("Query required for hybrid search")
                    return

                if not config.semantic_search_enabled:
                    print_error("Semantic search is not enabled")
                    return

                from ...storage.vector_store import VectorStore
                vector_store = VectorStore(config.vector_db_path)

                with console.status("[bold blue]Performing hybrid search..."):
                    entries = search_service.search_hybrid(
                        query=query,
                        vector_store=vector_store,
                        limit=limit,
                        entry_types=list(entry_types) if entry_types else None,
                        tags=list(tags) if tags else None
                    )

                if entries:
                    print_entries_table(entries, show_preview=True)
                    console.print("\n[dim]Hybrid search (semantic + keyword)[/dim]")
                else:
                    print_warning("No entries found")

            # Handle recent entries
            elif recent:
                entries = search_service.get_recent_entries(
                    limit=recent,
                    entry_types=list(entry_types) if entry_types else None
                )

                if entries:
                    print_entries_table(entries, show_preview=True)
                else:
                    print_warning("No entries found")

            # Handle standard search
            else:
                entries = search_service.search(
                    query=query,
                    entry_types=list(entry_types) if entry_types else None,
                    tags=list(tags) if tags else None,
                    projects=list(projects) if projects else None,
                    date_from=date_from,
                    date_to=date_to,
                    limit=limit
                )

                if entries:
                    print_entries_table(entries, show_preview=True)

                    if show_content and confirm_action("Show full entries?"):
                        console.print("\n")
                        for entry in entries:
                            print_entry(entry)
                            console.print("\n")
                else:
                    print_warning("No entries found")

    except Exception as e:
        print_error(f"Search failed: {str(e)}")
        raise

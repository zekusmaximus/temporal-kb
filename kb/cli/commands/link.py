# kb/cli/commands/link.py

import click

from ...core.database import get_db
from ...core.models import Entry
from ...core.schemas import LinkType
from ...services.entry_service import EntryService
from ...services.link_service import LinkService
from ...storage.file_manager import FileManager
from ..ui import (
    confirm_action,
    console,
    print_error,
    print_graph_stats,
    print_success,
    print_warning,
)


@click.group()
def link():
    """Manage links between entries"""
    pass

@link.command()
@click.argument('from_entry_id')
@click.argument('to_entry_id')
@click.option('--type', 'link_type',
              type=click.Choice([t.value for t in LinkType]),
              default='references',
              help='Link type')
@click.option('--context', '-c', help='Context for the link')
def create(from_entry_id, to_entry_id, link_type, context):
    """Create a link between two entries

    Examples:
        kb link create ent_abc123 ent_def456
        kb link create ent_abc123 ent_def456 --type builds_on
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            link_service = LinkService(session)

            link = link_service.create_link(
                from_entry_id=from_entry_id,
                to_entry_id=to_entry_id,
                link_type=LinkType(link_type),
                context=context,
                is_automatic=False
            )

            if link:
                print_success(f"✓ Link created: {link_type}")
            else:
                print_error("Failed to create link")

    except Exception as e:
        print_error(f"Link creation failed: {str(e)}")
        raise

@link.command()
@click.argument('entry_id')
@click.option('--min-strength', default=0.5, help='Minimum link strength (0-1)')
def detect(entry_id, min_strength):
    """Detect potential links for an entry

    Examples:
        kb link detect ent_abc123
        kb link detect ent_abc123 --min-strength 0.7
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            file_manager = FileManager()
            entry_service = EntryService(session, file_manager)
            link_service = LinkService(session)

            entry = entry_service.get_entry(entry_id)
            if not entry:
                print_error(f"Entry not found: {entry_id}")
                return

            with console.status("[bold blue]Detecting potential links..."):
                suggestions = link_service.suggest_links_for_entry(entry, limit=20)

            if not suggestions:
                print_warning("No potential links detected")
                return

            # Display suggestions
            from rich.table import Table

            table = Table(title=f"Potential Links for: {entry.title}")
            table.add_column("To Entry", style="cyan", width=40)
            table.add_column("Type", width=15)
            table.add_column("Strength", width=10, justify="right")
            table.add_column("Reason", width=30)

            for suggestion in suggestions:
                table.add_row(
                    suggestion['to_entry_title'][:40],
                    suggestion['link_type'].value,
                    f"{suggestion['strength']:.2f}",
                    suggestion['reason']
                )

            console.print(table)

            # Offer to create links
            if confirm_action("\nCreate these links automatically?"):
                count = link_service.auto_link_entry(entry, min_strength)
                print_success(f"✓ Created {count} links")

    except Exception as e:
        print_error(f"Link detection failed: {str(e)}")
        raise

@link.command()
@click.option('--min-strength', default=0.6, help='Minimum link strength (0-1)')
def auto_all(min_strength):
    """Auto-link all entries

    This will scan all entries and create automatic links.
    Useful after bulk imports or initial setup.
    """

    db = get_db()

    if not confirm_action(
        "[yellow]Auto-link all entries?[/yellow]\n"
        "This may take several minutes for large knowledge bases.",
        default=False
    ):
        print_warning("Auto-linking cancelled")
        return

    try:
        with console.status("[bold blue]Auto-linking all entries..."):
            with db.session_scope() as session:
                link_service = LinkService(session)
                count = link_service.auto_link_all_entries(min_strength)

        print_success(f"✓ Created {count} automatic links")

    except Exception as e:
        print_error(f"Auto-linking failed: {str(e)}")
        raise

@link.command()
@click.argument('entry_id')
@click.option('--limit', '-n', default=10, help='Max results')
def related(entry_id, limit):
    """Find entries related to this entry

    Examples:
        kb link related ent_abc123
        kb link related ent_abc123 --limit 20
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            file_manager = FileManager()
            entry_service = EntryService(session, file_manager)
            link_service = LinkService(session)

            entry = entry_service.get_entry(entry_id)
            if not entry:
                print_error(f"Entry not found: {entry_id}")
                return

            with console.status("[bold blue]Finding related entries..."):
                related = link_service.find_related_entries(entry, max_results=limit)

            if not related:
                print_warning("No related entries found")
                return

            # Display results
            from rich.table import Table

            table = Table(title=f"Related to: {entry.title}")
            table.add_column("Entry", style="cyan", width=50)
            table.add_column("Score", width=10, justify="right")

            for related_entry, score in related:
                table.add_row(
                    related_entry.title[:50],
                    f"{score:.2f}"
                )

            console.print(table)

    except Exception as e:
        print_error(f"Related search failed: {str(e)}")
        raise

@link.command()
def stats():
    """Show knowledge graph statistics"""

    db = get_db()

    try:
        with db.session_scope() as session:
            link_service = LinkService(session)
            stats = link_service.get_graph_stats()

        print_graph_stats(stats)

        # Show most connected entries
        if stats['most_connected']:
            console.print("\n[bold cyan]Most Connected Entries:[/bold cyan]")
            for item in stats['most_connected'][:10]:
                console.print(f"  {item['title'][:60]}: {item['link_count']} links")

    except Exception as e:
        print_error(f"Failed to get stats: {str(e)}")
        raise

@link.command()
@click.option('--min-size', default=3, help='Minimum cluster size')
def clusters(min_size):
    """Find clusters of interconnected entries"""

    db = get_db()

    try:
        with console.status("[bold blue]Finding clusters..."):
            with db.session_scope() as session:
                link_service = LinkService(session)
                clusters = link_service.find_clusters(min_cluster_size=min_size)

                # Get entry titles
                all_entry_ids = [eid for cluster in clusters for eid in cluster]
                entries = session.query(Entry).filter(Entry.id.in_(all_entry_ids)).all()
                entry_dict = {e.id: e for e in entries}

        if not clusters:
            print_warning(f"No clusters found with minimum size {min_size}")
            return

        console.print(f"\n[bold cyan]Found {len(clusters)} clusters:[/bold cyan]\n")

        for i, cluster in enumerate(clusters, 1):
            console.print(f"[bold]Cluster {i}[/bold] ({len(cluster)} entries):")
            for entry_id in cluster[:10]:  # Show first 10
                if entry_id in entry_dict:
                    console.print(f"  • {entry_dict[entry_id].title}")
            if len(cluster) > 10:
                console.print(f"  ... and {len(cluster) - 10} more")
            console.print()

    except Exception as e:
        print_error(f"Cluster analysis failed: {str(e)}")
        raise

# kb/cli/commands/show.py

import click
from ...core.database import get_db
from ...services.entry_service import EntryService
from ...storage.file_manager import FileManager
from ..ui import console, print_entry, print_error, print_versions_table, confirm_action


@click.command()
@click.argument("entry_id")
@click.option("--version", "-v", type=int, help="Show specific version")
@click.option("--history", "-h", is_flag=True, help="Show version history")
def show(entry_id, version, history):
    """Show a specific entry

    Examples:
        kb show ent_a1b2c3d4e5f6
        kb show ent_a1b2c3d4e5f6 --history
        kb show ent_a1b2c3d4e5f6 --version 3
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            file_manager = FileManager()
            entry_service = EntryService(session, file_manager)

            entry = entry_service.get_entry(entry_id)
            if not entry:
                print_error(f"Entry not found: {entry_id}")
                return

            if history:
                # Show version history
                versions = entry_service.get_entry_versions(entry_id)
                print_versions_table(versions)

                if confirm_action("View a specific version?"):
                    version_num = click.prompt("Version number", type=int)
                    content = entry_service.get_version_content(entry_id, version_num)
                    if content:
                        console.print(
                            Panel(
                                Markdown(content),
                                title=f"Version {version_num}",
                                border_style="yellow",
                            )
                        )
                    else:
                        print_error(f"Version {version_num} not found")

            elif version:
                # Show specific version
                content = entry_service.get_version_content(entry_id, version)
                if content:
                    from rich.panel import Panel
                    from rich.markdown import Markdown

                    console.print(
                        Panel(
                            Markdown(content),
                            title=f"{entry.title} (Version {version})",
                            border_style="yellow",
                        )
                    )
                else:
                    print_error(f"Version {version} not found")

            else:
                # Show current entry
                print_entry(entry)

                # Show links if any
                if entry.outgoing_links:
                    console.print("\n[bold cyan]Links to:[/bold cyan]")
                    for link in entry.outgoing_links[:5]:
                        console.print(f"  → {link.to_entry.title} ({link.link_type})")

                if entry.incoming_links:
                    console.print("\n[bold cyan]Linked from:[/bold cyan]")
                    for link in entry.incoming_links[:5]:
                        console.print(f"  ← {link.from_entry.title} ({link.link_type})")

    except Exception as e:
        print_error(f"Failed to show entry: {str(e)}")
        raise

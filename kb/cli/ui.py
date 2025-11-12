# kb/cli/ui.py

from typing import List

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()

def print_success(message: str):
    """Print success message in green"""
    console.print(f"[bold green]{message}[/bold green]")

def print_error(message: str):
    """Print error message in red"""
    console.print(f"[bold red]✗ {message}[/bold red]")

def print_warning(message: str):
    """Print warning message in yellow"""
    console.print(f"[bold yellow]⚠ {message}[/bold yellow]")

def print_info(message: str):
    """Print info message in blue"""
    console.print(f"[bold blue]ℹ {message}[/bold blue]")

def print_entry(entry, show_content: bool = True, show_metadata: bool = True):
    """Display a single entry with rich formatting"""

    # Header
    header = f"[bold cyan]{entry.title}[/bold cyan]"
    if show_metadata:
        header += f"\n[dim]ID: {entry.id} | Type: {entry.entry_type}[/dim]"
        header += f"\n[dim]Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')} | "
        header += f"Updated: {entry.updated_at.strftime('%Y-%m-%d %H:%M')}[/dim]"

    # Tags and projects
    if show_metadata:
        if entry.tags:
            tags_str = " ".join([f"[yellow]#{tag.name}[/yellow]" for tag in entry.tags])
            header += f"\n{tags_str}"
        if entry.projects:
            projects_str = " ".join([f"[magenta]@{proj.name}[/magenta]" for proj in entry.projects])
            header += f"\n{projects_str}"

    # Content
    content = ""
    if show_content:
        # Render markdown
        md = Markdown(entry.content)
        content = md

    # Panel
    panel = Panel(
        content if show_content else "",
        title=header,
        border_style="blue",
        padding=(1, 2)
    )

    console.print(panel)

def print_entries_table(entries: List, show_preview: bool = False):
    """Display entries in a table format"""

    if not entries:
        print_warning("No entries found")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Title", style="cyan", width=40)
    table.add_column("Type", width=15)
    table.add_column("Tags", width=20)
    table.add_column("Updated", width=16)

    if show_preview:
        table.add_column("Preview", width=40)

    for entry in entries:
        tags = ", ".join([f"#{tag.name}" for tag in entry.tags[:3]])
        if len(entry.tags) > 3:
            tags += f" +{len(entry.tags) - 3}"

        row = [
            entry.id[:12],
            entry.title[:40],
            entry.entry_type,
            tags or "[dim]none[/dim]",
            entry.updated_at.strftime('%Y-%m-%d %H:%M')
        ]

        if show_preview:
            preview = entry.content[:80].replace('\n', ' ')
            if len(entry.content) > 80:
                preview += "..."
            row.append(f"[dim]{preview}[/dim]")

        table.add_row(*row)

    console.print(table)
    console.print(f"\n[dim]Showing {len(entries)} entries[/dim]")

def print_versions_table(versions: List):
    """Display version history in a table"""

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Version", style="cyan", width=8)
    table.add_column("Changed", width=16)
    table.add_column("Type", width=12)
    table.add_column("Summary", width=50)

    for version in versions:
        table.add_row(
            str(version.version_number),
            version.changed_at.strftime('%Y-%m-%d %H:%M'),
            version.change_type or "",
            version.change_summary or "[dim]none[/dim]"
        )

    console.print(table)

def print_graph_stats(stats: dict):
    """Display graph statistics"""
    table = Table(title="Knowledge Graph Statistics", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white", justify="right")

    for key, value in stats.items():
        table.add_row(key, str(value))

    console.print(table)

def prompt_for_editor(initial_content: str = "") -> str:
    """Open system editor for content input"""
    import os
    import subprocess
    import tempfile

    # Determine editor
    editor = os.environ.get('EDITOR', 'vim')

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as tf:
        tf.write(initial_content)
        tf.flush()
        temp_path = tf.name

    try:
        # Open editor
        subprocess.call([editor, temp_path])

        # Read result
        with open(temp_path, 'r') as f:
            content = f.read()

        return content
    finally:
        os.unlink(temp_path)

def confirm_action(message: str, default: bool = False) -> bool:
    """Prompt user for confirmation"""
    return Confirm.ask(message, default=default)

def prompt_text(message: str, default: str = "") -> str:
    """Prompt user for text input"""
    return Prompt.ask(message, default=default)

def prompt_choice(message: str, choices: List[str]) -> str:
    """Prompt user to choose from options"""
    return Prompt.ask(message, choices=choices)

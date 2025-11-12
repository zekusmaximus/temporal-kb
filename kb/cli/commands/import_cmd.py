# kb/cli/commands/import_cmd.py

import click
from pathlib import Path
from datetime import datetime, timedelta

from ...core.database import get_db
from ...services.import_service import ImportService
from ...storage.file_manager import FileManager
from ..ui import console, print_success, print_error, print_info, print_warning, confirm_action


@click.group(name="import")
def import_data():
    """Import data from various sources"""
    pass


@import_data.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--recursive", "-r", is_flag=True, help="Scan subdirectories")
@click.option("--tag", "-t", multiple=True, help="Add tags to imported entries")
@click.option("--project", "-p", help="Associate with project")
def markdown(source, recursive, tag, project):
    """Import markdown files

    Examples:
        kb import markdown ~/Documents/notes --recursive
        kb import markdown ./research --tag research --project "AI Ethics"
    """

    db = get_db()

    try:
        with console.status("[bold blue]Importing markdown files..."):
            with db.session_scope() as session:
                file_manager = FileManager()
                import_service = ImportService(session, file_manager)

                importer = import_service.get_importer("markdown")
                stats = importer.import_data(
                    source=Path(source),
                    recursive=recursive,
                    tags=list(tag) if tag else None,
                    project=project,
                )

        # Display results
        print_success(f"✓ Import complete")
        print_info(f"Files found: {stats['files_found']}")
        print_info(f"Files imported: {stats['files_imported']}")

        if stats["files_skipped"] > 0:
            print_warning(f"Files skipped: {stats['files_skipped']}")

        if stats["errors"]:
            print_error("\nErrors:")
            for error in stats["errors"][:10]:
                console.print(f"  • {error}")

    except Exception as e:
        print_error(f"Import failed: {str(e)}")
        raise


@import_data.command()
@click.option("--server", required=True, help="IMAP server (e.g., imap.gmail.com)")
@click.option("--username", required=True, help="Email address")
@click.option("--password", required=True, help="App password")
@click.option("--folder", default="INBOX", help="Email folder")
@click.option("--since", help="Import emails since date (YYYY-MM-DD)")
@click.option("--sender", help="Filter by sender email")
@click.option("--label", multiple=True, help="Gmail labels to filter")
@click.option("--limit", default=100, help="Maximum emails to import")
def email(server, username, password, folder, since, sender, label, limit):
    """Import emails from IMAP server

    Examples:
        kb import email --server imap.gmail.com --username you@gmail.com --password "app-password"
        kb import email --server imap.gmail.com --username you@gmail.com --password "app-password" --since 2024-01-01
        kb import email --server imap.gmail.com --username you@gmail.com --password "app-password" --sender "colleague@company.com"
    """

    db = get_db()

    try:
        # Parse date
        since_date = None
        if since:
            since_date = datetime.strptime(since, "%Y-%m-%d")

        with console.status(f"[bold blue]Importing emails from {folder}..."):
            with db.session_scope() as session:
                file_manager = FileManager()
                import_service = ImportService(session, file_manager)

                importer = import_service.get_importer("email")
                stats = importer.import_data(
                    source=server,
                    username=username,
                    password=password,
                    folder=folder,
                    since_date=since_date,
                    labels=list(label) if label else None,
                    sender_filter=sender,
                    limit=limit,
                )

        # Display results
        print_success(f"✓ Email import complete")
        print_info(f"Emails found: {stats['emails_found']}")
        print_info(f"Emails imported: {stats['emails_imported']}")

        if stats["emails_skipped"] > 0:
            print_warning(f"Emails skipped: {stats['emails_skipped']}")

        if stats["errors"]:
            print_error("\nErrors:")
            for error in stats["errors"][:10]:
                console.print(f"  • {error}")

    except Exception as e:
        print_error(f"Email import failed: {str(e)}")
        raise


@import_data.command()
@click.argument("source", type=click.Path())
@click.option("--browser", type=click.Choice(["chrome", "firefox", "safari"]), default="chrome")
@click.option("--since", help="Import history since date (YYYY-MM-DD)")
@click.option("--url-filter", help="Filter URLs containing text")
@click.option("--limit", default=500, help="Maximum visits to import")
def browser(source, browser, since, url_filter, limit):
    """Import browser history

    Examples:
        kb import browser auto --browser chrome --since 2024-11-01
        kb import browser ~/Library/Application\\ Support/Google/Chrome/Default/History
    """

    db = get_db()

    try:
        # Parse date
        since_date = None
        if since:
            since_date = datetime.strptime(since, "%Y-%m-%d")

        with console.status(f"[bold blue]Importing {browser} history..."):
            with db.session_scope() as session:
                file_manager = FileManager()
                import_service = ImportService(session, file_manager)

                importer = import_service.get_importer("browser")
                stats = importer.import_data(
                    source=source,
                    browser=browser,
                    since_date=since_date,
                    url_filter=url_filter,
                    limit=limit,
                )

        # Display results
        print_success(f"✓ Browser history import complete")
        print_info(f"Visits found: {stats['visits_found']}")
        print_info(f"Visits imported: {stats['visits_imported']}")

        if stats["visits_skipped"] > 0:
            print_warning(f"Visits skipped: {stats['visits_skipped']}")

        if stats["errors"]:
            print_error("\nErrors:")
            for error in stats["errors"][:5]:
                console.print(f"  • {error}")

    except Exception as e:
        print_error(f"Browser import failed: {str(e)}")
        raise


@import_data.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["auto", "claude", "chatgpt"]), default="auto")
@click.option("--tag", "-t", multiple=True, help="Add tags to imported chats")
def chat(source, format, tag):
    """Import chat conversation exports

    Examples:
        kb import chat ~/Downloads/claude_conversations
        kb import chat ./chatgpt_export.json --format chatgpt
    """

    db = get_db()

    try:
        with console.status("[bold blue]Importing chat conversations..."):
            with db.session_scope() as session:
                file_manager = FileManager()
                import_service = ImportService(session, file_manager)

                importer = import_service.get_importer("chat")
                stats = importer.import_data(
                    source=Path(source), chat_format=format, tags=list(tag) if tag else None
                )

        # Display results
        print_success(f"✓ Chat import complete")
        print_info(f"Conversations found: {stats['conversations_found']}")
        print_info(f"Conversations imported: {stats['conversations_imported']}")

        if stats["conversations_skipped"] > 0:
            print_warning(f"Conversations skipped: {stats['conversations_skipped']}")

        if stats["errors"]:
            print_error("\nErrors:")
            for error in stats["errors"][:10]:
                console.print(f"  • {error}")

    except Exception as e:
        print_error(f"Chat import failed: {str(e)}")
        raise

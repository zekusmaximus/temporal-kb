# kb/cli/commands/temporal.py

from datetime import datetime

import click

from ...core.database import get_db
from ...services.temporal_service import TemporalService
from ..ui import console, print_entries_table, print_error, print_info


@click.group()
def temporal():
    """Temporal queries and time-based analysis"""
    pass

@temporal.command(name='on-this-day')
def on_this_day():
    """Show entries created on this day in history

    Example:
        kb temporal on-this-day
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            temporal_service = TemporalService(session)
            entries = temporal_service.get_entries_on_this_day()

        if not entries:
            print_info("No entries found for this day in history")
            return

        today = datetime.now().strftime('%B %d')
        console.print(f"\n[bold cyan]On This Day ({today}):[/bold cyan]\n")

        # Group by year
        by_year = {}
        for entry in entries:
            year = entry.created_at.year
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(entry)

        for year in sorted(by_year.keys(), reverse=True):
            console.print(f"[bold]{year}:[/bold]")
            for entry in by_year[year]:
                console.print(f"  • {entry.title}")
            console.print()

    except Exception as e:
        print_error(f"Query failed: {str(e)}")
        raise

@temporal.command()
@click.option('--start', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end', required=True, help='End date (YYYY-MM-DD)')
def range(start, end):
    """Show entries from a date range

    Examples:
        kb temporal range --start 2024-01-01 --end 2024-01-31
    """

    db = get_db()

    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')

        with db.session_scope() as session:
            temporal_service = TemporalService(session)
            entries = temporal_service.get_entries_in_range(start_date, end_date)

        if entries:
            print_entries_table(entries, show_preview=True)
        else:
            print_info(f"No entries found between {start} and {end}")

    except ValueError:
        print_error("Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        print_error(f"Query failed: {str(e)}")
        raise

@temporal.command()
@click.option('--period1-start', required=True, help='Period 1 start (YYYY-MM-DD)')
@click.option('--period1-end', required=True, help='Period 1 end (YYYY-MM-DD)')
@click.option('--period2-start', required=True, help='Period 2 start (YYYY-MM-DD)')
@click.option('--period2-end', required=True, help='Period 2 end (YYYY-MM-DD)')
def compare(period1_start, period1_end, period2_start, period2_end):
    """Compare two time periods (then vs now)

    Examples:
        kb temporal compare \
          --period1-start 2023-01-01 --period1-end 2023-03-31 \
          --period2-start 2024-01-01 --period2-end 2024-03-31
    """

    db = get_db()

    try:
        p1_start = datetime.strptime(period1_start, '%Y-%m-%d')
        p1_end = datetime.strptime(period1_end, '%Y-%m-%d')
        p2_start = datetime.strptime(period2_start, '%Y-%m-%d')
        p2_end = datetime.strptime(period2_end, '%Y-%m-%d')

        with db.session_scope() as session:
            temporal_service = TemporalService(session)
            comparison = temporal_service.compare_periods(
                p1_start, p1_end, p2_start, p2_end
            )

        # Display comparison
        from rich.panel import Panel
        from rich.table import Table

        console.print(Panel(
            f"[bold]Period 1:[/bold] {period1_start} to {period1_end}\n"
            f"[bold]Period 2:[/bold] {period2_start} to {period2_end}",
            title="Comparison",
            border_style="cyan"
        ))

        # Summary table
        table = Table(title="Overview")
        table.add_column("Metric", style="cyan")
        table.add_column("Period 1", justify="right")
        table.add_column("Period 2", justify="right")
        table.add_column("Change", justify="right")

        p1 = comparison['period1']['stats']
        p2 = comparison['period2']['stats']
        changes = comparison['changes']

        table.add_row(
            "Entries",
            str(p1['count']),
            str(p2['count']),
            f"{changes['entry_count_change']:+d} ({changes['entry_count_change_pct']:+.1f}%)"
        )

        table.add_row(
            "Total Words",
            f"{p1['total_words']:,}",
            f"{p2['total_words']:,}",
            f"{changes['word_count_change']:+,} ({changes['word_count_change_pct']:+.1f}%)"
        )

        table.add_row(
            "Avg Words/Entry",
            f"{p1['avg_words_per_entry']:.0f}",
            f"{p2['avg_words_per_entry']:.0f}",
            f"{p2['avg_words_per_entry'] - p1['avg_words_per_entry']:+.0f}"
        )

        console.print(table)

        # Changes
        if changes['new_tags']:
            console.print(f"\n[bold green]New tags:[/bold green] {', '.join(changes['new_tags'])}")
        if changes['lost_tags']:
            console.print(f"[bold red]Lost tags:[/bold red] {', '.join(changes['lost_tags'])}")
        if changes['new_projects']:
            console.print(f"\n[bold green]New projects:[/bold green] {', '.join(changes['new_projects'])}")
        if changes['lost_projects']:
            console.print(f"[bold red]Lost projects:[/bold red] {', '.join(changes['lost_projects'])}")

    except ValueError:
        print_error("Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        print_error(f"Comparison failed: {str(e)}")
        raise

@temporal.command()
@click.argument('topic')
@click.option('--tag', '-t', help='Filter by tag')
def evolution(topic, tag):
    """Track how your thinking on a topic evolved over time

    Examples:
        kb temporal evolution "consciousness"
        kb temporal evolution "digital rebirth" --tag fiction
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            temporal_service = TemporalService(session)

            # Get first entry matching topic
            from ...services.entry_service import EntryService
            from ...storage.file_manager import FileManager
            EntryService(session, FileManager())

            # Find entries on topic
            evolution = temporal_service.get_evolution_of_topic(topic, tag)

        if not evolution:
            print_info(f"No entries found for topic: {topic}")
            return

        console.print(f"\n[bold cyan]Evolution of: {topic}[/bold cyan]\n")

        for _i, item in enumerate(evolution):
            entry = item['entry']
            date = item['date'].strftime('%Y-%m-%d')

            if item['time_since_last']:
                days = item['time_since_last'].days
                console.print(f"[dim]↓ {days} days later[/dim]")

            console.print(f"[bold]{date}[/bold] - {entry.title}")

            # Show preview
            preview = entry.content[:200].replace('\n', ' ')
            console.print(f"  [dim]{preview}...[/dim]\n")

    except Exception as e:
        print_error(f"Evolution query failed: {str(e)}")
        raise

@temporal.command()
def patterns():
    """Analyze temporal patterns in your knowledge base

    Example:
        kb temporal patterns
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            temporal_service = TemporalService(session)
            patterns = temporal_service.get_temporal_patterns()

        from rich.table import Table

        # Most productive times
        console.print("\n[bold cyan]Your Most Productive Times:[/bold cyan]\n")

        if patterns['most_productive_day']:
            console.print(f"Day: [bold]{patterns['most_productive_day']}[/bold]")
        if patterns['most_productive_hour']:
            hour = patterns['most_productive_hour']
            time_str = f"{hour:02d}:00-{hour+1:02d}:00"
            console.print(f"Hour: [bold]{time_str}[/bold]")
        if patterns['most_productive_season']:
            console.print(f"Season: [bold]{patterns['most_productive_season']}[/bold]")

        # Weekday distribution
        console.print("\n[bold cyan]Activity by Weekday:[/bold cyan]")
        weekday_table = Table(show_header=False)
        weekday_table.add_column("Day", style="cyan")
        weekday_table.add_column("Entries", justify="right")

        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days_order:
            count = patterns['by_weekday'].get(day, 0)
            weekday_table.add_row(day, str(count))

        console.print(weekday_table)

        # Season distribution
        console.print("\n[bold cyan]Activity by Season:[/bold cyan]")
        season_table = Table(show_header=False)
        season_table.add_column("Season", style="cyan")
        season_table.add_column("Entries", justify="right")

        for season in ['Winter', 'Spring', 'Summer', 'Fall']:
            count = patterns['by_season'].get(season, 0)
            season_table.add_row(season, str(count))

        console.print(season_table)

    except Exception as e:
        print_error(f"Pattern analysis failed: {str(e)}")
        raise

@temporal.command()
@click.option('--interval', type=click.Choice(['day', 'week', 'month', 'year']), default='month')
def growth(interval):
    """Show knowledge base growth over time

    Examples:
        kb temporal growth
        kb temporal growth --interval week
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            temporal_service = TemporalService(session)
            timeline = temporal_service.get_growth_timeline(interval)

        if not timeline:
            print_info("No growth data available")
            return

        from rich.table import Table

        table = Table(title=f"Growth Timeline ({interval}ly)")
        table.add_column("Period", style="cyan")
        table.add_column("New", justify="right")
        table.add_column("Total", justify="right")
        table.add_column("Words", justify="right")

        # Show last 20 periods
        for item in timeline[-20:]:
            table.add_row(
                item['period'],
                str(item['new_entries']),
                str(item['cumulative_entries']),
                f"{item['cumulative_words']:,}"
            )

        console.print(table)

        # Summary
        timeline[0]
        last = timeline[-1]
        total_periods = len(timeline)
        avg_per_period = last['cumulative_entries'] / total_periods

        console.print("\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"  Total {interval}s: {total_periods}")
        console.print(f"  Average entries per {interval}: {avg_per_period:.1f}")
        console.print(f"  Total growth: {last['cumulative_entries']} entries, {last['cumulative_words']:,} words")

    except Exception as e:
        print_error(f"Growth analysis failed: {str(e)}")
        raise

@temporal.command()
def cyclical():
    """Find topics that recur at regular intervals

    Example:
        kb temporal cyclical
    """

    db = get_db()

    try:
        with db.session_scope() as session:
            temporal_service = TemporalService(session)
            patterns = temporal_service.find_cyclical_topics(min_occurrences=3)

        if not patterns:
            print_info("No cyclical patterns detected")
            return

        from rich.table import Table

        table = Table(title="Cyclical Topics")
        table.add_column("Tag", style="cyan")
        table.add_column("Occurrences", justify="right")
        table.add_column("Pattern", style="yellow")
        table.add_column("Last", style="dim")
        table.add_column("Next Expected", style="green")

        for pattern in patterns:
            table.add_row(
                pattern['tag'],
                str(pattern['occurrences']),
                pattern['pattern'],
                pattern['last_occurrence'].strftime('%Y-%m-%d'),
                pattern['next_expected'].strftime('%Y-%m-%d')
            )

        console.print(table)

    except Exception as e:
        print_error(f"Cyclical analysis failed: {str(e)}")
        raise



# kb/services/temporal_service.py

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from collections import defaultdict
import calendar

from ..core.models import Entry, EntryVersion, Tag, Project


class TemporalService:
    """
    Provides temporal intelligence and "then vs now" analysis
    """

    def __init__(self, session: Session):
        self.session = session

    def get_entries_on_date(self, date: datetime, exact_match: bool = False) -> List[Entry]:
        """
        Get entries from a specific date

        Args:
            date: Target date
            exact_match: If True, match exact date; if False, match day regardless of year

        Returns:
            List of entries
        """
        if exact_match:
            start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

            return (
                self.session.query(Entry)
                .filter(and_(Entry.created_at >= start, Entry.created_at < end))
                .order_by(Entry.created_at)
                .all()
            )
        else:
            # Same day/month across all years
            return (
                self.session.query(Entry)
                .filter(
                    and_(
                        extract("month", Entry.created_at) == date.month,
                        extract("day", Entry.created_at) == date.day,
                    )
                )
                .order_by(Entry.created_at.desc())
                .all()
            )

    def get_entries_on_this_day(self) -> List[Entry]:
        """Get all entries created on this day in history"""
        return self.get_entries_on_date(datetime.now(), exact_match=False)

    def get_entries_in_range(self, start_date: datetime, end_date: datetime) -> List[Entry]:
        """Get entries created within a date range"""
        return (
            self.session.query(Entry)
            .filter(and_(Entry.created_at >= start_date, Entry.created_at <= end_date))
            .order_by(Entry.created_at)
            .all()
        )

    def compare_periods(
        self,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
    ) -> Dict[str, Any]:
        """
        Compare two time periods
        Useful for "then vs now" analysis

        Returns:
            Comparison statistics
        """
        # Get entries from both periods
        period1_entries = self.get_entries_in_range(period1_start, period1_end)
        period2_entries = self.get_entries_in_range(period2_start, period2_end)

        # Analyze entry types
        def analyze_period(entries: List[Entry]) -> Dict[str, Any]:
            types = defaultdict(int)
            tags = defaultdict(int)
            projects = defaultdict(int)
            word_count = 0

            for entry in entries:
                types[entry.entry_type] += 1
                word_count += entry.word_count or 0

                for tag in entry.tags:
                    tags[tag.name] += 1

                for project in entry.projects:
                    projects[project.name] += 1

            return {
                "count": len(entries),
                "types": dict(types),
                "top_tags": dict(sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]),
                "top_projects": dict(
                    sorted(projects.items(), key=lambda x: x[1], reverse=True)[:10]
                ),
                "total_words": word_count,
                "avg_words_per_entry": word_count / len(entries) if entries else 0,
            }

        period1_stats = analyze_period(period1_entries)
        period2_stats = analyze_period(period2_entries)

        # Calculate changes
        entry_change = period2_stats["count"] - period1_stats["count"]
        entry_change_pct = (
            (entry_change / period1_stats["count"] * 100) if period1_stats["count"] > 0 else 0
        )

        word_change = period2_stats["total_words"] - period1_stats["total_words"]
        word_change_pct = (
            (word_change / period1_stats["total_words"] * 100)
            if period1_stats["total_words"] > 0
            else 0
        )

        # Find new and lost tags/projects
        period1_tags = set(period1_stats["top_tags"].keys())
        period2_tags = set(period2_stats["top_tags"].keys())
        new_tags = period2_tags - period1_tags
        lost_tags = period1_tags - period2_tags

        period1_projects = set(period1_stats["top_projects"].keys())
        period2_projects = set(period2_stats["top_projects"].keys())
        new_projects = period2_projects - period1_projects
        lost_projects = period1_projects - period2_projects

        return {
            "period1": {"start": period1_start, "end": period1_end, "stats": period1_stats},
            "period2": {"start": period2_start, "end": period2_end, "stats": period2_stats},
            "changes": {
                "entry_count_change": entry_change,
                "entry_count_change_pct": round(entry_change_pct, 1),
                "word_count_change": word_change,
                "word_count_change_pct": round(word_change_pct, 1),
                "new_tags": list(new_tags),
                "lost_tags": list(lost_tags),
                "new_projects": list(new_projects),
                "lost_projects": list(lost_projects),
            },
        }

    def get_evolution_of_topic(self, topic: str, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Track how your thinking on a topic has evolved over time

        Args:
            topic: Topic to search for
            tag: Optional tag to filter by

        Returns:
            List of entries sorted chronologically with analysis
        """
        query = self.session.query(Entry).filter(
            or_(Entry.title.ilike(f"%{topic}%"), Entry.content.ilike(f"%{topic}%"))
        )

        if tag:
            query = query.join(Entry.tags).filter(Tag.name == tag)

        entries = query.order_by(Entry.created_at).all()

        # Analyze evolution
        evolution = []
        for i, entry in enumerate(entries):
            item = {
                "entry": entry,
                "date": entry.created_at,
                "version_number": i + 1,
                "time_since_last": None,
            }

            if i > 0:
                time_diff = entry.created_at - entries[i - 1].created_at
                item["time_since_last"] = time_diff

            evolution.append(item)

        return evolution

    def get_activity_heatmap(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        Get activity heatmap (entries per day)

        Returns:
            Dict mapping date strings to entry counts
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()

        entries = self.get_entries_in_range(start_date, end_date)

        heatmap = defaultdict(int)
        for entry in entries:
            date_key = entry.created_at.strftime("%Y-%m-%d")
            heatmap[date_key] += 1

        return dict(heatmap)

    def get_temporal_patterns(self) -> Dict[str, Any]:
        """
        Analyze temporal patterns in knowledge base

        Returns:
            Statistics about temporal patterns
        """
        all_entries = self.session.query(Entry).all()

        # Day of week analysis
        weekday_counts = defaultdict(int)
        for entry in all_entries:
            weekday = entry.created_at.strftime("%A")
            weekday_counts[weekday] += 1

        # Hour of day analysis
        hour_counts = defaultdict(int)
        for entry in all_entries:
            hour = entry.created_at.hour
            hour_counts[hour] += 1

        # Month analysis
        month_counts = defaultdict(int)
        for entry in all_entries:
            month = entry.created_at.strftime("%B")
            month_counts[month] += 1

        # Seasonal analysis
        season_counts = defaultdict(int)
        for entry in all_entries:
            month = entry.created_at.month
            if month in [12, 1, 2]:
                season = "Winter"
            elif month in [3, 4, 5]:
                season = "Spring"
            elif month in [6, 7, 8]:
                season = "Summer"
            else:
                season = "Fall"
            season_counts[season] += 1

        return {
            "by_weekday": dict(weekday_counts),
            "by_hour": dict(hour_counts),
            "by_month": dict(month_counts),
            "by_season": dict(season_counts),
            "most_productive_day": (
                max(weekday_counts.items(), key=lambda x: x[1])[0] if weekday_counts else None
            ),
            "most_productive_hour": (
                max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
            ),
            "most_productive_season": (
                max(season_counts.items(), key=lambda x: x[1])[0] if season_counts else None
            ),
        }

    def get_growth_timeline(self, interval: str = "month") -> List[Dict[str, Any]]:
        """
        Get knowledge base growth over time

        Args:
            interval: 'day', 'week', 'month', or 'year'

        Returns:
            Timeline data
        """
        all_entries = self.session.query(Entry).order_by(Entry.created_at).all()

        if not all_entries:
            return []

        timeline = []
        cumulative_count = 0
        cumulative_words = 0

        # Group entries by interval
        groups = defaultdict(list)
        for entry in all_entries:
            if interval == "day":
                key = entry.created_at.strftime("%Y-%m-%d")
            elif interval == "week":
                key = entry.created_at.strftime("%Y-W%W")
            elif interval == "month":
                key = entry.created_at.strftime("%Y-%m")
            else:  # year
                key = entry.created_at.strftime("%Y")

            groups[key].append(entry)

        # Build timeline
        for key in sorted(groups.keys()):
            entries_in_period = groups[key]
            period_count = len(entries_in_period)
            period_words = sum(e.word_count or 0 for e in entries_in_period)

            cumulative_count += period_count
            cumulative_words += period_words

            timeline.append(
                {
                    "period": key,
                    "new_entries": period_count,
                    "new_words": period_words,
                    "cumulative_entries": cumulative_count,
                    "cumulative_words": cumulative_words,
                }
            )

        return timeline

    def get_entry_lifespan_stats(self) -> Dict[str, Any]:
        """
        Analyze how long entries remain active (get updated)
        """
        entries_with_updates = (
            self.session.query(Entry).filter(Entry.created_at != Entry.updated_at).all()
        )

        lifespans = []
        for entry in entries_with_updates:
            lifespan = (entry.updated_at - entry.created_at).days
            lifespans.append(lifespan)

        if not lifespans:
            return {
                "entries_with_updates": 0,
                "avg_lifespan_days": 0,
                "max_lifespan_days": 0,
                "min_lifespan_days": 0,
            }

        return {
            "entries_with_updates": len(lifespans),
            "avg_lifespan_days": sum(lifespans) / len(lifespans),
            "max_lifespan_days": max(lifespans),
            "min_lifespan_days": min(lifespans),
        }

    def find_cyclical_topics(self, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """
        Find topics that recur at regular intervals
        Useful for identifying seasonal interests

        Returns:
            List of cyclical patterns
        """
        # Get all tags with their entry dates
        tag_dates = defaultdict(list)

        entries = self.session.query(Entry).all()
        for entry in entries:
            for tag in entry.tags:
                tag_dates[tag.name].append(entry.created_at)

        # Analyze for cyclical patterns
        cyclical = []
        for tag_name, dates in tag_dates.items():
            if len(dates) < min_occurrences:
                continue

            # Sort dates
            dates.sort()

            # Calculate intervals between occurrences
            intervals = []
            for i in range(1, len(dates)):
                days_diff = (dates[i] - dates[i - 1]).days
                intervals.append(days_diff)

            if not intervals:
                continue

            # Check for regular patterns
            avg_interval = sum(intervals) / len(intervals)

            # Consider it cyclical if intervals are somewhat regular
            variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
            std_dev = variance**0.5

            # If std dev is less than 30% of mean, consider it cyclical
            if std_dev < (avg_interval * 0.3) and avg_interval > 7:  # More than a week
                cyclical.append(
                    {
                        "tag": tag_name,
                        "occurrences": len(dates),
                        "avg_interval_days": round(avg_interval, 1),
                        "pattern": self._describe_interval(avg_interval),
                        "last_occurrence": dates[-1],
                        "next_expected": dates[-1] + timedelta(days=avg_interval),
                    }
                )

        return sorted(cyclical, key=lambda x: x["occurrences"], reverse=True)

    def _describe_interval(self, days: float) -> str:
        """Convert day interval to human-readable pattern"""
        if days < 10:
            return f"~{int(days)} days"
        elif 25 <= days <= 35:
            return "Monthly"
        elif 85 <= days <= 95:
            return "Quarterly"
        elif 160 <= days <= 200:
            return "Semi-annually"
        elif 350 <= days <= 380:
            return "Annually"
        else:
            return f"~{int(days)} days"

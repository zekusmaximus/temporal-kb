# kb/api/routes/temporal.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_session
from ...core.schemas import EntryResponse
from ...services.temporal_service import TemporalService
from ..dependencies import get_current_user

router = APIRouter()


def get_temporal_service(db: Session = Depends(get_session)):
    return TemporalService(db)


@router.get("/on-this-day", response_model=List[EntryResponse])
async def on_this_day(
    temporal_service: TemporalService = Depends(get_temporal_service),
    current_user: dict = Depends(get_current_user),
):
    """Get entries created on this day in history"""

    entries = temporal_service.get_entries_on_this_day()

    return [
        EntryResponse(
            id=entry.id,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            entry_type=entry.entry_type,
            title=entry.title,
            content=entry.content[:200],  # Preview
            tags=[tag.name for tag in entry.tags],
            projects=[proj.name for proj in entry.projects],
            version_count=len(entry.versions),
        )
        for entry in entries
    ]


@router.get("/range", response_model=List[EntryResponse])
async def date_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    temporal_service: TemporalService = Depends(get_temporal_service),
    current_user: dict = Depends(get_current_user),
):
    """Get entries from a date range"""

    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from e

    entries = temporal_service.get_entries_in_range(start, end)

    return [
        EntryResponse(
            id=entry.id,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            entry_type=entry.entry_type,
            title=entry.title,
            content=entry.content[:200],
            tags=[tag.name for tag in entry.tags],
            projects=[proj.name for proj in entry.projects],
            version_count=len(entry.versions),
        )
        for entry in entries
    ]


@router.get("/compare")
async def compare_periods(
    period1_start: str = Query(..., description="Period 1 start (YYYY-MM-DD)"),
    period1_end: str = Query(..., description="Period 1 end (YYYY-MM-DD)"),
    period2_start: str = Query(..., description="Period 2 start (YYYY-MM-DD)"),
    period2_end: str = Query(..., description="Period 2 end (YYYY-MM-DD)"),
    temporal_service: TemporalService = Depends(get_temporal_service),
    current_user: dict = Depends(get_current_user),
):
    """Compare two time periods (then vs now)"""

    try:
        p1_start = datetime.fromisoformat(period1_start)
        p1_end = datetime.fromisoformat(period1_end)
        p2_start = datetime.fromisoformat(period2_start)
        p2_end = datetime.fromisoformat(period2_end)
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from e

    comparison = temporal_service.compare_periods(p1_start, p1_end, p2_start, p2_end)

    return comparison


@router.get("/evolution/{topic}")
async def topic_evolution(
    topic: str,
    tag: Optional[str] = None,
    temporal_service: TemporalService = Depends(get_temporal_service),
    current_user: dict = Depends(get_current_user),
):
    """Track how thinking on a topic evolved over time"""

    evolution = temporal_service.get_evolution_of_topic(topic, tag)

    return {
        "topic": topic,
        "tag": tag,
        "evolution": [
            {
                "entry_id": item["entry"].id,
                "title": item["entry"].title,
                "date": item["date"].isoformat(),
                "version_number": item["version_number"],
                "time_since_last_days": (
                    item["time_since_last"].days if item["time_since_last"] else None
                ),
            }
            for item in evolution
        ],
    }


@router.get("/patterns")
async def temporal_patterns(
    temporal_service: TemporalService = Depends(get_temporal_service),
    current_user: dict = Depends(get_current_user),
):
    """Analyze temporal patterns in knowledge base"""

    patterns = temporal_service.get_temporal_patterns()
    return patterns


@router.get("/growth")
async def growth_timeline(
    interval: str = Query("month", regex="^(day|week|month|year)$"),
    temporal_service: TemporalService = Depends(get_temporal_service),
    current_user: dict = Depends(get_current_user),
):
    """Get knowledge base growth over time"""

    timeline = temporal_service.get_growth_timeline(interval)
    return {"interval": interval, "timeline": timeline}


@router.get("/cyclical")
async def cyclical_topics(
    min_occurrences: int = Query(3, ge=2),
    temporal_service: TemporalService = Depends(get_temporal_service),
    current_user: dict = Depends(get_current_user),
):
    """Find topics that recur at regular intervals"""

    patterns = temporal_service.find_cyclical_topics(min_occurrences)
    return {"patterns": patterns}


@router.get("/heatmap")
async def activity_heatmap(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    temporal_service: TemporalService = Depends(get_temporal_service),
    current_user: dict = Depends(get_current_user),
):
    """Get activity heatmap (entries per day)"""

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    heatmap = temporal_service.get_activity_heatmap(start, end)

    return {"heatmap": heatmap}

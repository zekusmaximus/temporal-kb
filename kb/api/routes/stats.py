# kb/api/routes/stats.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...core.database import get_session
from ...core.models import Entry, Tag, Project, EntryLink
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/overview")
async def overview_stats(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get overview statistics"""
    
    total_entries = db.query(func.count(Entry.id)).scalar()
    total_words = db.query(func.sum(Entry.word_count)).scalar() or 0
    total_tags = db.query(func.count(Tag.id)).scalar()
    total_projects = db.query(func.count(Project.id)).scalar()
    total_links = db.query(func.count(EntryLink.id)).scalar()
    
    # Entry type distribution
    type_dist = db.query(
        Entry.entry_type,
        func.count(Entry.id).label('count')
    )\
        .group_by(Entry.entry_type)\
        .all()
    
    return {
        "total_entries": total_entries,
        "total_words": total_words,
        "total_tags": total_tags,
        "total_projects": total_projects,
        "total_links": total_links,
        "avg_words_per_entry": total_words / total_entries if total_entries > 0 else 0,
        "entry_type_distribution": {et: count for et, count in type_dist}
    }



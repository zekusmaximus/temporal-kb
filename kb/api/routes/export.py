from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
import json
from datetime import datetime

from ...core.database import get_session
from ...services.entry_service import EntryService
from ...storage.file_manager import FileManager
from ..dependencies import get_current_user

router = APIRouter()


@router.get("/json")
async def export_json(
    db: Session = Depends(get_session), current_user: dict = Depends(get_current_user)
):
    """Export all entries as JSON"""

    from ...core.models import Entry

    entries = db.query(Entry).all()

    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "version": "1.0",
        "entries": [
            {
                "id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "entry_type": entry.entry_type,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
                "tags": [tag.name for tag in entry.tags],
                "projects": [proj.name for proj in entry.projects],
            }
            for entry in entries
        ],
    }

    return Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=kb_export_{datetime.now().strftime('%Y%m%d')}.json"
        },
    )

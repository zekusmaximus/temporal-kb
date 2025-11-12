# kb/api/routes/tags.py


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_session
from ...core.models import EntryTag, Tag
from ...core.schemas import TagCreate
from ..dependencies import get_current_user

router = APIRouter()


@router.get("/")
async def list_tags(
    db: Session = Depends(get_session), current_user: dict = Depends(get_current_user)
):
    """List all tags with usage counts"""

    from sqlalchemy import func

    tags = (
        db.query(
            Tag.id, Tag.name, Tag.category, Tag.color, func.count(EntryTag.entry_id).label("count")
        )
        .outerjoin(EntryTag)
        .group_by(Tag.id)
        .order_by(func.count(EntryTag.entry_id).desc())
        .all()
    )

    return [
        {
            "id": tag.id,
            "name": tag.name,
            "category": tag.category,
            "color": tag.color,
            "usage_count": tag.count,
        }
        for tag in tags
    ]


@router.post("/")
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Create a new tag"""

    # Check if exists
    existing = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Tag already exists")

    tag = Tag(
        name=tag_data.name,
        category=tag_data.category,
        color=tag_data.color,
        parent_tag_id=tag_data.parent_tag_id,
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return {"id": tag.id, "name": tag.name, "category": tag.category, "color": tag.color}

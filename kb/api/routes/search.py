# kb/api/routes/search.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...core.database import get_session
from ...core.schemas import EntryResponse, SearchQuery, EntryType
from ...services.search_service import SearchService
from ...storage.vector_store import VectorStore
from ...core.config import get_config
from ..dependencies import get_current_user

router = APIRouter()


def get_search_service(db: Session = Depends(get_session)):
    return SearchService(db)


@router.get("/", response_model=List[EntryResponse])
async def search_entries(
    q: Optional[str] = Query(None, description="Search query"),
    entry_types: Optional[List[str]] = Query(None, description="Filter by entry types"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    projects: Optional[List[str]] = Query(None, description="Filter by projects"),
    date_from: Optional[str] = Query(None, description="From date (ISO format)"),
    date_to: Optional[str] = Query(None, description="To date (ISO format)"),
    limit: int = Query(50, ge=1, le=500, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search_service: SearchService = Depends(get_search_service),
    current_user: dict = Depends(get_current_user),
):
    """
    Search entries with filters

    - **q**: Search text (searches title and content)
    - **entry_types**: Filter by entry types
    - **tags**: Filter by tags (AND logic)
    - **projects**: Filter by projects
    - **date_from**: ISO format datetime string
    - **date_to**: ISO format datetime string
    - **limit**: Maximum results (1-500)
    - **offset**: Pagination offset
    """

    entries = search_service.search(
        query=q,
        entry_types=entry_types,
        tags=tags,
        projects=projects,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    return [
        EntryResponse(
            id=entry.id,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            entry_type=entry.entry_type,
            title=entry.title,
            content=entry.content,
            source=entry.source,
            source_metadata=entry.source_metadata,
            word_count=entry.word_count,
            file_path=entry.file_path,
            vault_id=entry.vault_id,
            is_public=entry.is_public,
            tags=[tag.name for tag in entry.tags],
            projects=[proj.name for proj in entry.projects],
            version_count=len(entry.versions),
        )
        for entry in entries
    ]


@router.get("/semantic", response_model=List[dict])
async def semantic_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
):
    """
    Semantic search using vector embeddings

    Returns entries with similarity scores
    """

    config = get_config()

    if not config.semantic_search_enabled:
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Semantic search is not enabled")

    vector_store = VectorStore(config.vector_db_path)
    results = vector_store.search(q, limit=limit)

    # Fetch full entries
    if results:
        from ...core.models import Entry

        db = next(get_session())

        entry_ids = [r["id"] for r in results]
        entries = db.query(Entry).filter(Entry.id.in_(entry_ids)).all()
        entries_dict = {e.id: e for e in entries}

        # Combine with similarity scores
        response = []
        for result in results:
            if result["id"] in entries_dict:
                entry = entries_dict[result["id"]]
                response.append(
                    {
                        "entry": EntryResponse(
                            id=entry.id,
                            created_at=entry.created_at,
                            updated_at=entry.updated_at,
                            entry_type=entry.entry_type,
                            title=entry.title,
                            content=entry.content[:500],  # Truncate for API
                            source=entry.source,
                            word_count=entry.word_count,
                            file_path=entry.file_path,
                            is_public=entry.is_public,
                            tags=[tag.name for tag in entry.tags],
                            projects=[proj.name for proj in entry.projects],
                            version_count=len(entry.versions),
                        ),
                        "similarity_score": result["similarity"],
                    }
                )

        return response

    return []


@router.get("/recent", response_model=List[EntryResponse])
async def recent_entries(
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    entry_types: Optional[List[str]] = Query(None, description="Filter by entry types"),
    search_service: SearchService = Depends(get_search_service),
    current_user: dict = Depends(get_current_user),
):
    """Get most recently updated entries"""

    entries = search_service.get_recent_entries(limit=limit, entry_types=entry_types)

    return [
        EntryResponse(
            id=entry.id,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            entry_type=entry.entry_type,
            title=entry.title,
            content=entry.content,
            source=entry.source,
            word_count=entry.word_count,
            tags=[tag.name for tag in entry.tags],
            projects=[proj.name for proj in entry.projects],
            version_count=len(entry.versions),
        )
        for entry in entries
    ]


@router.get("/orphaned", response_model=List[EntryResponse])
async def orphaned_entries(
    search_service: SearchService = Depends(get_search_service),
    current_user: dict = Depends(get_current_user),
):
    """Find entries with no tags, projects, or links"""

    entries = search_service.get_orphaned_entries()

    return [
        EntryResponse(
            id=entry.id,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            entry_type=entry.entry_type,
            title=entry.title,
            content=entry.content,
            source=entry.source,
            word_count=entry.word_count,
            tags=[],
            projects=[],
            version_count=len(entry.versions),
        )
        for entry in entries
    ]

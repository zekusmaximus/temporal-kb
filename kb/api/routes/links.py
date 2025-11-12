# kb/api/routes/links.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...core.database import get_session
from ...core.schemas import LinkCreate, LinkResponse, LinkType
from ...services.link_service import LinkService
from ..dependencies import get_current_user

router = APIRouter()

def get_link_service(db: Session = Depends(get_session)):
    return LinkService(db)


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    link_data: LinkCreate,
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a link between two entries"""
    
    link = link_service.create_link(
        from_entry_id=link_data.from_entry_id,
        to_entry_id=link_data.to_entry_id,
        link_type=link_data.link_type,
        context=link_data.context,
        is_automatic=False
    )
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create link"
        )
    
    return LinkResponse(
        id=link.id,
        from_entry_id=link.from_entry_id,
        to_entry_id=link.to_entry_id,
        link_type=link.link_type,
        strength=link.strength,
        created_at=link.created_at
    )


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: str,
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Delete a link"""
    
    success = link_service.delete_link(link_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link not found: {link_id}"
        )
    
    return None


@router.get("/from/{entry_id}", response_model=List[LinkResponse])
async def get_links_from_entry(
    entry_id: str,
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Get all outgoing links from an entry"""
    
    links = link_service.get_links_from_entry(entry_id)
    
    return [
        LinkResponse(
            id=link.id,
            from_entry_id=link.from_entry_id,
            to_entry_id=link.to_entry_id,
            link_type=link.link_type,
            strength=link.strength,
            created_at=link.created_at
        )
        for link in links
    ]


@router.get("/to/{entry_id}", response_model=List[LinkResponse])
async def get_links_to_entry(
    entry_id: str,
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Get all incoming links to an entry"""
    
    links = link_service.get_links_to_entry(entry_id)
    
    return [
        LinkResponse(
            id=link.id,
            from_entry_id=link.from_entry_id,
            to_entry_id=link.to_entry_id,
            link_type=link.link_type,
            strength=link.strength,
            created_at=link.created_at
        )
        for link in links
    ]


@router.post("/{entry_id}/detect")
async def detect_links(
    entry_id: str,
    min_strength: float = 0.5,
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Detect and suggest potential links for an entry"""
    
    from ...services.entry_service import EntryService
    from ...storage.file_manager import FileManager
    
    db = next(get_session())
    entry_service = EntryService(db, FileManager())
    
    entry = entry_service.get_entry(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry not found: {entry_id}"
        )
    
    suggestions = link_service.suggest_links_for_entry(entry, limit=20)
    
    return {
        "entry_id": entry_id,
        "suggestions": suggestions
    }


@router.post("/{entry_id}/auto-link")
async def auto_link_entry(
    entry_id: str,
    min_strength: float = 0.5,
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Automatically create links for an entry"""
    
    from ...services.entry_service import EntryService
    from ...storage.file_manager import FileManager
    
    db = next(get_session())
    entry_service = EntryService(db, FileManager())
    
    entry = entry_service.get_entry(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry not found: {entry_id}"
        )
    
    count = link_service.auto_link_entry(entry, min_strength)
    
    return {
        "entry_id": entry_id,
        "links_created": count
    }


@router.get("/{entry_id}/related")
async def find_related(
    entry_id: str,
    max_results: int = 10,
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Find entries related to this entry"""
    
    from ...services.entry_service import EntryService
    from ...storage.file_manager import FileManager
    from ...core.schemas import EntryResponse
    
    db = next(get_session())
    entry_service = EntryService(db, FileManager())
    
    entry = entry_service.get_entry(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry not found: {entry_id}"
        )
    
    related = link_service.find_related_entries(entry, max_results=max_results)
    
    return [
        {
            "entry": EntryResponse(
                id=rel_entry.id,
                created_at=rel_entry.created_at,
                updated_at=rel_entry.updated_at,
                entry_type=rel_entry.entry_type,
                title=rel_entry.title,
                content=rel_entry.content[:200],  # Preview
                tags=[tag.name for tag in rel_entry.tags],
                projects=[proj.name for proj in rel_entry.projects],
                version_count=len(rel_entry.versions)
            ),
            "relevance_score": score
        }
        for rel_entry, score in related
    ]


@router.get("/graph/stats")
async def graph_stats(
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Get knowledge graph statistics"""
    
    stats = link_service.get_graph_stats()
    return stats


@router.get("/graph/clusters")
async def find_clusters(
    min_size: int = 3,
    link_service: LinkService = Depends(get_link_service),
    current_user: dict = Depends(get_current_user)
):
    """Find clusters of interconnected entries"""
    
    clusters = link_service.find_clusters(min_cluster_size=min_size)
    
    # Get entry titles for clusters
    from ...core.models import Entry
    db = next(get_session())
    
    all_entry_ids = [eid for cluster in clusters for eid in cluster]
    entries = db.query(Entry).filter(Entry.id.in_(all_entry_ids)).all()
    entry_dict = {e.id: {'id': e.id, 'title': e.title} for e in entries}
    
    result = []
    for cluster in clusters:
        result.append({
            'size': len(cluster),
            'entries': [entry_dict[eid] for eid in cluster if eid in entry_dict]
        })
    
    return {"clusters": result}
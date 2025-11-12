# kb/api/routes/entries.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...core.database import get_session
from ...core.schemas import (
    EntryCreate, EntryUpdate, EntryResponse, 
    EntryVersionResponse, EntryType
)
from ...services.entry_service import EntryService
from ...storage.file_manager import FileManager
from ..dependencies import get_current_user

router = APIRouter()

def get_entry_service(db: Session = Depends(get_session)):
    return EntryService(db, FileManager())


@router.post("/", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(
    entry_data: EntryCreate,
    entry_service: EntryService = Depends(get_entry_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new entry"""
    try:
        entry = entry_service.create_entry(entry_data)
        
        # Convert to response model
        response = EntryResponse(
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
            version_count=len(entry.versions)
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific entry"""
    entry = entry_service.get_entry(entry_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry not found: {entry_id}"
        )
    
    response = EntryResponse(
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
        version_count=len(entry.versions)
    )
    
    return response


@router.put("/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: str,
    update_data: EntryUpdate,
    entry_service: EntryService = Depends(get_entry_service),
    current_user: dict = Depends(get_current_user)
):
    """Update an entry"""
    try:
        entry = entry_service.update_entry(entry_id, update_data)
        
        response = EntryResponse(
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
            version_count=len(entry.versions)
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
    current_user: dict = Depends(get_current_user)
):
    """Delete an entry"""
    success = entry_service.delete_entry(entry_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry not found: {entry_id}"
        )
    
    return None


@router.get("/{entry_id}/versions", response_model=List[EntryVersionResponse])
async def get_entry_versions(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
    current_user: dict = Depends(get_current_user)
):
    """Get version history for an entry"""
    versions = entry_service.get_entry_versions(entry_id)
    
    if not versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry not found: {entry_id}"
        )
    
    return [
        EntryVersionResponse(
            id=v.id,
            version_number=v.version_number,
            changed_at=v.changed_at,
            change_type=v.change_type,
            change_summary=v.change_summary
        )
        for v in versions
    ]


@router.get("/{entry_id}/versions/{version_number}")
async def get_version_content(
    entry_id: str,
    version_number: int,
    entry_service: EntryService = Depends(get_entry_service),
    current_user: dict = Depends(get_current_user)
):
    """Get content from a specific version"""
    content = entry_service.get_version_content(entry_id, version_number)
    
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found for entry {entry_id}"
        )
    
    return {"content": content, "version_number": version_number}
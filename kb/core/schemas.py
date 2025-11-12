# kb/core/schemas.py

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class EntryType(str, Enum):
    NOTE = "note"
    LEGAL_CASE = "legal_case"
    CODE_SNIPPET = "code_snippet"
    CONCEPT = "concept"
    MEETING_NOTE = "meeting_note"
    BOOK_HIGHLIGHT = "book_highlight"
    WEB_CLIP = "web_clip"
    CHAT_EXPORT = "chat_export"


class LinkType(str, Enum):
    REFERENCES = "references"
    BUILDS_ON = "builds_on"
    CONTRADICTS = "contradicts"
    APPLIES_TO = "applies_to"
    INSPIRED_BY = "inspired_by"


class EntryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str
    entry_type: EntryType
    source: Optional[str] = None
    source_metadata: Optional[Dict[str, Any]] = None
    vault_id: Optional[str] = None
    is_public: bool = False


class EntryCreate(EntryBase):
    tags: Optional[List[str]] = []
    projects: Optional[List[str]] = []


class EntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    is_public: Optional[bool] = None


class EntryResponse(EntryBase):
    id: str
    created_at: datetime
    updated_at: datetime
    word_count: int
    file_path: Optional[str]
    tags: List[str] = []
    projects: List[str] = []
    version_count: int = 0

    class Config:
        from_attributes = True


class EntryVersionResponse(BaseModel):
    id: str
    version_number: int
    changed_at: datetime
    change_type: str
    change_summary: Optional[str]

    class Config:
        from_attributes = True


class LinkCreate(BaseModel):
    from_entry_id: str
    to_entry_id: str
    link_type: LinkType
    context: Optional[str] = None


class LinkResponse(BaseModel):
    id: str
    from_entry_id: str
    to_entry_id: str
    link_type: str
    strength: float
    created_at: datetime

    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    query: str
    entry_types: Optional[List[EntryType]] = None
    tags: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)
    semantic: bool = False  # Use vector search


class TemporalQuery(BaseModel):
    query: str
    date: Optional[datetime] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    comparison_mode: bool = False  # Compare "then vs now"


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None
    color: Optional[str] = None
    parent_tag_id: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    project_type: str
    description: Optional[str] = None
    parent_project_id: Optional[str] = None

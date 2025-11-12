# kb/services/search_service.py

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import Session

from ..core.models import Entry, EntryProject, EntryTag, Project, Tag

if TYPE_CHECKING:
    from ..storage.vector_store import VectorStore


class SearchService:
    def __init__(self, session: Session):
        self.session = session

    def search(
        self,
        query: Optional[str] = None,
        entry_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        projects: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Entry]:
        """
        Perform full-text and filtered search on entries

        Args:
            query: Search text (searches title and content)
            entry_types: Filter by entry types
            tags: Filter by tags (AND logic - entry must have all tags)
            projects: Filter by projects
            date_from: ISO format datetime string
            date_to: ISO format datetime string
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching Entry objects
        """

        # Start with base query
        q = self.session.query(Entry)

        # Full-text search
        if query:
            search_term = f"%{query}%"
            q = q.filter(or_(Entry.title.ilike(search_term), Entry.content.ilike(search_term)))

        # Filter by entry types
        if entry_types:
            q = q.filter(Entry.entry_type.in_(entry_types))

        # Filter by tags (must have ALL specified tags)
        if tags:
            for tag_name in tags:
                tag_subq = (
                    self.session.query(EntryTag.entry_id)
                    .join(Tag)
                    .filter(Tag.name == tag_name)
                    .subquery()
                )
                q = q.filter(Entry.id.in_(tag_subq))

        # Filter by projects
        if projects:
            project_subq = (
                self.session.query(EntryProject.entry_id)
                .join(Project)
                .filter(Project.name.in_(projects))
                .subquery()
            )
            q = q.filter(Entry.id.in_(project_subq))

        # Date range filters
        if date_from:
            dt_from = datetime.fromisoformat(date_from)
            q = q.filter(Entry.created_at >= dt_from)

        if date_to:
            dt_to = datetime.fromisoformat(date_to)
            q = q.filter(Entry.created_at <= dt_to)

        # Order by relevance (updated_at for now, can be enhanced)
        q = q.order_by(Entry.updated_at.desc())

        # Apply pagination
        q = q.limit(limit).offset(offset)

        return q.all()

    def search_fts(self, query: str, limit: int = 50) -> List[Entry]:
        """
        Full-text search using SQLite FTS5
        More efficient than LIKE for large datasets

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching Entry objects ordered by relevance
        """

        # Use FTS5 virtual table for search
        fts_query = text(
            """
            SELECT entry_id, rank
            FROM entries_fts
            WHERE entries_fts MATCH :query
            ORDER BY rank
            LIMIT :limit
        """
        )

        results = self.session.execute(fts_query, {"query": query, "limit": limit}).fetchall()

        if not results:
            return []

        # Get full entries preserving rank order
        entry_ids = [r[0] for r in results]
        entries = self.session.query(Entry).filter(Entry.id.in_(entry_ids)).all()

        # Sort by original rank order
        entry_dict = {e.id: e for e in entries}
        sorted_entries = [entry_dict[eid] for eid in entry_ids if eid in entry_dict]

        return sorted_entries

    def search_by_date_range(
        self, start_date: datetime, end_date: datetime, entry_types: Optional[List[str]] = None
    ) -> List[Entry]:
        """
        Search entries within a specific date range
        Useful for temporal queries
        """

        q = self.session.query(Entry).filter(
            and_(Entry.created_at >= start_date, Entry.created_at <= end_date)
        )

        if entry_types:
            q = q.filter(Entry.entry_type.in_(entry_types))

        return q.order_by(Entry.created_at.desc()).all()

    def find_similar_titles(
        self, title: str, threshold: float = 0.6, limit: int = 10
    ) -> List[Entry]:
        """
        Find entries with similar titles
        Uses simple string similarity (Levenshtein distance)
        """

        # For SQLite, we'll use a simple LIKE approach
        # For production, consider using a proper similarity function
        title_pattern = f"%{title}%"

        entries = (
            self.session.query(Entry).filter(Entry.title.ilike(title_pattern)).limit(limit).all()
        )

        return entries

    def get_entries_with_tag(self, tag_name: str) -> List[Entry]:
        """Get all entries with a specific tag"""

        return (
            self.session.query(Entry)
            .join(Entry.tags)
            .filter(Tag.name == tag_name)
            .order_by(Entry.updated_at.desc())
            .all()
        )

    def get_entries_in_project(self, project_name: str) -> List[Entry]:
        """Get all entries in a specific project"""

        return (
            self.session.query(Entry)
            .join(Entry.projects)
            .filter(Project.name == project_name)
            .order_by(Entry.updated_at.desc())
            .all()
        )

    def get_recent_entries(
        self, limit: int = 20, entry_types: Optional[List[str]] = None
    ) -> List[Entry]:
        """Get most recently updated entries"""

        q = self.session.query(Entry).order_by(Entry.updated_at.desc())

        if entry_types:
            q = q.filter(Entry.entry_type.in_(entry_types))

        return q.limit(limit).all()

    def get_popular_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most frequently used tags"""

        results = (
            self.session.query(Tag.name, func.count(EntryTag.entry_id).label("count"))
            .join(EntryTag)
            .group_by(Tag.name)
            .order_by(func.count(EntryTag.entry_id).desc())
            .limit(limit)
            .all()
        )

        return [{"name": name, "count": count} for name, count in results]

    def get_orphaned_entries(self) -> List[Entry]:
        """
        Find entries with no tags, no projects, and no links
        Useful for cleanup and organization
        """

        from ..core.models import EntryLink

        entries = (
            self.session.query(Entry)
            .outerjoin(EntryTag)
            .outerjoin(EntryProject)
            .outerjoin(
                EntryLink,
                or_(Entry.id == EntryLink.from_entry_id, Entry.id == EntryLink.to_entry_id),
            )
            .filter(
                and_(
                    EntryTag.entry_id.is_(None),
                    EntryProject.entry_id.is_(None),
                    EntryLink.id.is_(None),
                )
            )
            .all()
        )

        return entries

    def count_entries(
        self, entry_types: Optional[List[str]] = None, tags: Optional[List[str]] = None
    ) -> int:
        """Count entries matching filters"""

        q = self.session.query(func.count(Entry.id))

        if entry_types:
            q = q.filter(Entry.entry_type.in_(entry_types))

        if tags:
            for tag_name in tags:
                tag_subq = (
                    self.session.query(EntryTag.entry_id)
                    .join(Tag)
                    .filter(Tag.name == tag_name)
                    .subquery()
                )
                q = q.filter(Entry.id.in_(tag_subq))

        return q.scalar()

    def search_hybrid(
        self,
        query: str,
        vector_store: "VectorStore",
        limit: int = 50,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4,
        entry_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Entry]:
        """
        Hybrid search combining semantic and keyword search

        Args:
            query: Search query
            vector_store: VectorStore instance
            limit: Maximum results
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)
            entry_types: Filter by entry types
            tags: Filter by tags

        Returns:
            List of entries ranked by combined score
        """

        # Normalize weights
        total_weight = semantic_weight + keyword_weight
        semantic_weight /= total_weight
        keyword_weight /= total_weight

        # Get semantic results
        semantic_results = vector_store.search(query, limit=limit * 2)
        semantic_scores = {r["id"]: r["similarity"] * semantic_weight for r in semantic_results}

        # Get keyword results
        keyword_results = self.search_fts(query, limit=limit * 2)

        # Calculate keyword scores (simple inverse rank scoring)
        keyword_scores = {}
        for rank, entry in enumerate(keyword_results, 1):
            score = (1.0 / rank) * keyword_weight
            keyword_scores[entry.id] = score

        # Combine scores
        all_entry_ids = set(semantic_scores.keys()) | set(keyword_scores.keys())
        combined_scores = {}
        for entry_id in all_entry_ids:
            combined_scores[entry_id] = semantic_scores.get(entry_id, 0) + keyword_scores.get(
                entry_id, 0
            )

        # Get entries and sort by combined score
        sorted_ids = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)[
            :limit
        ]

        # Fetch full entries
        entries = self.session.query(Entry).filter(Entry.id.in_(sorted_ids)).all()

        # Apply filters if specified
        if entry_types:
            entries = [e for e in entries if e.entry_type in entry_types]

        if tags:
            entries = [e for e in entries if all(tag in {t.name for t in e.tags} for tag in tags)]

        # Sort by combined score
        entry_dict = {e.id: e for e in entries}
        sorted_entries = [entry_dict[eid] for eid in sorted_ids if eid in entry_dict]

        return sorted_entries

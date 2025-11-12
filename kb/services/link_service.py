# kb/services/link_service.py

from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
import re
from collections import defaultdict
import logging

from ..core.models import Entry, EntryLink, Tag, Project
from ..core.schemas import LinkType

logger = logging.getLogger(__name__)

class LinkService:
    """
    Manages relationships between entries
    Provides automatic link detection and graph analysis
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_link(
        self,
        from_entry_id: str,
        to_entry_id: str,
        link_type: LinkType,
        context: Optional[str] = None,
        strength: float = 1.0,
        is_automatic: bool = False
    ) -> Optional[EntryLink]:
        """
        Create a link between two entries
        
        Args:
            from_entry_id: Source entry ID
            to_entry_id: Target entry ID
            link_type: Type of relationship
            context: Surrounding text where link was mentioned
            strength: Link strength (0-1)
            is_automatic: Whether link was auto-detected
        
        Returns:
            Created EntryLink or None
        """
        try:
            # Check if link already exists
            existing = self.session.query(EntryLink).filter(
                and_(
                    EntryLink.from_entry_id == from_entry_id,
                    EntryLink.to_entry_id == to_entry_id,
                    EntryLink.link_type == link_type.value
                )
            ).first()
            
            if existing:
                # Update strength if higher
                if strength > existing.strength:
                    existing.strength = strength
                    existing.context = context
                    self.session.commit()
                return existing
            
            # Create new link
            link = EntryLink(
                from_entry_id=from_entry_id,
                to_entry_id=to_entry_id,
                link_type=link_type.value,
                context=context,
                strength=strength,
                is_automatic=is_automatic
            )
            
            self.session.add(link)
            self.session.commit()
            
            logger.debug(f"Created link: {from_entry_id} -> {to_entry_id} ({link_type})")
            return link
        
        except Exception as e:
            logger.error(f"Failed to create link: {e}")
            self.session.rollback()
            return None
    
    def delete_link(self, link_id: str) -> bool:
        """Delete a link"""
        try:
            link = self.session.query(EntryLink).filter(EntryLink.id == link_id).first()
            if link:
                self.session.delete(link)
                self.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete link: {e}")
            self.session.rollback()
            return False
    
    def get_links_from_entry(self, entry_id: str) -> List[EntryLink]:
        """Get all outgoing links from an entry"""
        return self.session.query(EntryLink)\
            .filter(EntryLink.from_entry_id == entry_id)\
            .order_by(EntryLink.strength.desc())\
            .all()
    
    def get_links_to_entry(self, entry_id: str) -> List[EntryLink]:
        """Get all incoming links to an entry"""
        return self.session.query(EntryLink)\
            .filter(EntryLink.to_entry_id == entry_id)\
            .order_by(EntryLink.strength.desc())\
            .all()
    
    def detect_links_in_entry(self, entry: Entry, min_strength: float = 0.5) -> List[Dict[str, Any]]:
        """
        Automatically detect potential links in entry content
        
        Args:
            entry: Entry to analyze
            min_strength: Minimum link strength to create
        
        Returns:
            List of detected links with metadata
        """
        detected_links = []
        
        # Get all other entries
        other_entries = self.session.query(Entry)\
            .filter(Entry.id != entry.id)\
            .all()
        
        entry_text = f"{entry.title} {entry.content}".lower()
        
        for other_entry in other_entries:
            # Check for title mentions
            if other_entry.title.lower() in entry_text:
                # Find context
                pattern = re.compile(
                    f".{{0,50}}{re.escape(other_entry.title.lower())}.{{0,50}}",
                    re.IGNORECASE
                )
                match = pattern.search(entry_text)
                context = match.group(0) if match else None
                
                detected_links.append({
                    'to_entry_id': other_entry.id,
                    'to_entry_title': other_entry.title,
                    'link_type': LinkType.REFERENCES,
                    'strength': 0.8,
                    'context': context,
                    'reason': 'title_mention'
                })
            
            # Check for shared tags (weaker signal)
            if entry.tags and other_entry.tags:
                shared_tags = set(t.name for t in entry.tags) & set(t.name for t in other_entry.tags)
                if len(shared_tags) >= 2:  # At least 2 shared tags
                    strength = min(0.7, len(shared_tags) * 0.2)
                    detected_links.append({
                        'to_entry_id': other_entry.id,
                        'to_entry_title': other_entry.title,
                        'link_type': LinkType.REFERENCES,
                        'strength': strength,
                        'context': f"Shared tags: {', '.join(shared_tags)}",
                        'reason': 'shared_tags'
                    })
            
            # Check for shared projects
            if entry.projects and other_entry.projects:
                shared_projects = set(p.name for p in entry.projects) & set(p.name for p in other_entry.projects)
                if shared_projects:
                    detected_links.append({
                        'to_entry_id': other_entry.id,
                        'to_entry_title': other_entry.title,
                        'link_type': LinkType.APPLIES_TO,
                        'strength': 0.6,
                        'context': f"Shared project: {', '.join(shared_projects)}",
                        'reason': 'shared_project'
                    })
        
        # Filter by minimum strength
        detected_links = [link for link in detected_links if link['strength'] >= min_strength]
        
        # Remove duplicates (keep highest strength)
        unique_links = {}
        for link in detected_links:
            key = link['to_entry_id']
            if key not in unique_links or link['strength'] > unique_links[key]['strength']:
                unique_links[key] = link
        
        return list(unique_links.values())
    
    def auto_link_entry(self, entry: Entry, min_strength: float = 0.5) -> int:
        """
        Automatically create links for an entry
        
        Args:
            entry: Entry to link
            min_strength: Minimum link strength
        
        Returns:
            Number of links created
        """
        detected = self.detect_links_in_entry(entry, min_strength)
        created_count = 0
        
        for link_data in detected:
            link = self.create_link(
                from_entry_id=entry.id,
                to_entry_id=link_data['to_entry_id'],
                link_type=link_data['link_type'],
                context=link_data.get('context'),
                strength=link_data['strength'],
                is_automatic=True
            )
            if link:
                created_count += 1
        
        return created_count
    
    def auto_link_all_entries(self, min_strength: float = 0.6) -> int:
        """
        Run auto-linking on all entries
        Useful for initial setup or after bulk imports
        
        Returns:
            Total number of links created
        """
        entries = self.session.query(Entry).all()
        total_links = 0
        
        for entry in entries:
            count = self.auto_link_entry(entry, min_strength)
            total_links += count
        
        logger.info(f"Auto-linked {total_links} relationships across {len(entries)} entries")
        return total_links
    
    def find_related_entries(
        self,
        entry: Entry,
        max_results: int = 10,
        include_indirect: bool = True
    ) -> List[Tuple[Entry, float]]:
        """
        Find entries related to given entry
        Uses both direct links and indirect connections
        
        Args:
            entry: Reference entry
            max_results: Maximum results to return
            include_indirect: Include entries linked through intermediaries
        
        Returns:
            List of (Entry, relevance_score) tuples
        """
        related_scores = defaultdict(float)
        
        # Direct outgoing links
        for link in entry.outgoing_links:
            related_scores[link.to_entry_id] += link.strength * 1.0
        
        # Direct incoming links
        for link in entry.incoming_links:
            related_scores[link.from_entry_id] += link.strength * 0.8
        
        if include_indirect:
            # Indirect links (entries linked to my linked entries)
            for link in entry.outgoing_links:
                for indirect_link in link.to_entry.outgoing_links:
                    if indirect_link.to_entry_id != entry.id:
                        related_scores[indirect_link.to_entry_id] += \
                            link.strength * indirect_link.strength * 0.3
        
        # Get entries and sort by score
        sorted_entries = sorted(
            related_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:max_results]
        
        # Fetch full entries
        entry_ids = [eid for eid, _ in sorted_entries]
        entries = self.session.query(Entry).filter(Entry.id.in_(entry_ids)).all()
        entry_dict = {e.id: e for e in entries}
        
        results = [
            (entry_dict[eid], score)
            for eid, score in sorted_entries
            if eid in entry_dict
        ]
        
        return results
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        
        total_entries = self.session.query(func.count(Entry.id)).scalar()
        total_links = self.session.query(func.count(EntryLink.id)).scalar()
        
        # Entries with/without links
        entries_with_links = self.session.query(func.count(func.distinct(EntryLink.from_entry_id))).scalar()
        orphaned_entries = total_entries - entries_with_links
        
        # Average links per entry
        avg_links = total_links / total_entries if total_entries > 0 else 0
        
        # Most connected entries
        most_connected = self.session.query(
            Entry.id,
            Entry.title,
            func.count(EntryLink.id).label('link_count')
        )\
            .join(EntryLink, or_(
                Entry.id == EntryLink.from_entry_id,
                Entry.id == EntryLink.to_entry_id
            ))\
            .group_by(Entry.id)\
            .order_by(func.count(EntryLink.id).desc())\
            .limit(10)\
            .all()
        
        # Link types distribution
        link_types = self.session.query(
            EntryLink.link_type,
            func.count(EntryLink.id).label('count')
        )\
            .group_by(EntryLink.link_type)\
            .all()
        
        return {
            'total_entries': total_entries,
            'total_links': total_links,
            'entries_with_links': entries_with_links,
            'orphaned_entries': orphaned_entries,
            'avg_links_per_entry': round(avg_links, 2),
            'most_connected': [
                {'id': e.id, 'title': e.title, 'link_count': count}
                for e, _, count in most_connected
            ],
            'link_types': {lt: count for lt, count in link_types}
        }
    
    def find_clusters(self, min_cluster_size: int = 3) -> List[List[str]]:
        """
        Find clusters of highly interconnected entries
        Uses simple connected components algorithm
        
        Args:
            min_cluster_size: Minimum entries in a cluster
        
        Returns:
            List of clusters (each cluster is a list of entry IDs)
        """
        # Build adjacency list
        adjacency = defaultdict(set)
        
        links = self.session.query(EntryLink).all()
        for link in links:
            adjacency[link.from_entry_id].add(link.to_entry_id)
            adjacency[link.to_entry_id].add(link.from_entry_id)
        
        # Find connected components using DFS
        visited = set()
        clusters = []
        
        def dfs(node_id: str, cluster: Set[str]):
            visited.add(node_id)
            cluster.add(node_id)
            for neighbor in adjacency[node_id]:
                if neighbor not in visited:
                    dfs(neighbor, cluster)
        
        for entry_id in adjacency.keys():
            if entry_id not in visited:
                cluster = set()
                dfs(entry_id, cluster)
                if len(cluster) >= min_cluster_size:
                    clusters.append(list(cluster))
        
        # Sort clusters by size
        clusters.sort(key=len, reverse=True)
        
        return clusters
    
    def suggest_links_for_entry(
        self,
        entry: Entry,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Suggest potential links for an entry based on various signals
        Similar to detect_links but returns more detailed suggestions
        """
        suggestions = self.detect_links_in_entry(entry, min_strength=0.3)
        
        # Filter out existing links
        existing_links = {link.to_entry_id for link in entry.outgoing_links}
        suggestions = [s for s in suggestions if s['to_entry_id'] not in existing_links]
        
        # Sort by strength
        suggestions.sort(key=lambda x: x['strength'], reverse=True)
        
        return suggestions[:limit]
# kb/storage/vector_store.py

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from ..core.models import Entry

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages vector embeddings for semantic search using ChromaDB
    """

    def __init__(
        self,
        persist_directory: Path,
        model_name: str = "all-MiniLM-L6-v2",
        collection_name: str = "entries",
    ):
        """
        Initialize vector store

        Args:
            persist_directory: Directory to store ChromaDB data
            model_name: Sentence transformer model name
            collection_name: ChromaDB collection name
        """
        self.persist_directory = persist_directory
        self.model_name = model_name
        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(persist_directory),
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

        # Load sentence transformer model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded")

    def add_entry(self, entry: Entry) -> bool:
        """
        Add or update entry in vector store

        Args:
            entry: Entry object to add

        Returns:
            True if successful
        """
        try:
            # Prepare text for embedding
            text = self._prepare_text(entry)

            # Generate embedding
            embedding = self.model.encode(text).tolist()

            # Prepare metadata
            metadata = {
                "entry_id": entry.id,
                "title": entry.title,
                "entry_type": entry.entry_type,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
                "word_count": entry.word_count,
                "tags": ",".join([tag.name for tag in entry.tags]) if entry.tags else "",
                "projects": (
                    ",".join([proj.name for proj in entry.projects]) if entry.projects else ""
                ),
            }

            # Add to collection (upsert)
            self.collection.upsert(
                ids=[entry.id], embeddings=[embedding], documents=[text], metadatas=[metadata]
            )

            logger.debug(f"Added entry to vector store: {entry.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add entry to vector store: {e}")
            return False

    def add_entries_batch(self, entries: List[Entry], batch_size: int = 100) -> int:
        """
        Add multiple entries in batches

        Args:
            entries: List of Entry objects
            batch_size: Number of entries to process at once

        Returns:
            Number of successfully added entries
        """
        success_count = 0

        for i in range(0, len(entries), batch_size):
            batch = entries[i : i + batch_size]

            try:
                # Prepare batch data
                ids = [entry.id for entry in batch]
                texts = [self._prepare_text(entry) for entry in batch]
                embeddings = self.model.encode(texts).tolist()

                metadatas = []
                for entry in batch:
                    metadatas.append(
                        {
                            "entry_id": entry.id,
                            "title": entry.title,
                            "entry_type": entry.entry_type,
                            "created_at": entry.created_at.isoformat(),
                            "updated_at": entry.updated_at.isoformat(),
                            "word_count": entry.word_count,
                            "tags": (
                                ",".join([tag.name for tag in entry.tags]) if entry.tags else ""
                            ),
                            "projects": (
                                ",".join([proj.name for proj in entry.projects])
                                if entry.projects
                                else ""
                            ),
                        }
                    )

                # Upsert batch
                self.collection.upsert(
                    ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas
                )

                success_count += len(batch)
                logger.info(f"Added batch of {len(batch)} entries to vector store")

            except Exception as e:
                logger.error(f"Failed to add batch to vector store: {e}")

        return success_count

    def search(
        self, query: str, limit: int = 10, where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using query text

        Args:
            query: Search query text
            limit: Maximum number of results
            where: Metadata filters (e.g., {"entry_type": "legal_case"})

        Returns:
            List of results with id, distance, and metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()

            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=limit, where=where
            )

            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i, entry_id in enumerate(results["ids"][0]):
                    formatted_results.append(
                        {
                            "id": entry_id,
                            "distance": results["distances"][0][i],
                            "similarity": 1
                            - results["distances"][0][i],  # Convert distance to similarity
                            "metadata": results["metadatas"][0][i],
                            "document": results["documents"][0][i],
                        }
                    )

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def find_similar(
        self, entry_id: str, limit: int = 10, where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find entries similar to a given entry

        Args:
            entry_id: ID of the reference entry
            limit: Maximum number of results
            where: Metadata filters

        Returns:
            List of similar entries
        """
        try:
            # Get the entry's embedding
            result = self.collection.get(ids=[entry_id], include=["embeddings"])

            if not result["embeddings"]:
                logger.warning(f"Entry {entry_id} not found in vector store")
                return []

            embedding = result["embeddings"][0]

            # Search for similar entries
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=limit + 1,  # +1 to exclude the entry itself
                where=where,
            )

            # Format and filter out the original entry
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i, result_id in enumerate(results["ids"][0]):
                    if result_id != entry_id:  # Exclude the query entry itself
                        formatted_results.append(
                            {
                                "id": result_id,
                                "distance": results["distances"][0][i],
                                "similarity": 1 - results["distances"][0][i],
                                "metadata": results["metadatas"][0][i],
                                "document": results["documents"][0][i],
                            }
                        )

            return formatted_results[:limit]

        except Exception as e:
            logger.error(f"Similar search failed: {e}")
            return []

    def delete_entry(self, entry_id: str) -> bool:
        """
        Remove entry from vector store

        Args:
            entry_id: Entry ID to remove

        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[entry_id])
            logger.debug(f"Deleted entry from vector store: {entry_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete entry from vector store: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""

        count = self.collection.count()

        return {
            "collection_name": self.collection_name,
            "entry_count": count,
            "model_name": self.model_name,
            "persist_directory": str(self.persist_directory),
        }

    def rebuild_index(self, entries: List[Entry]) -> int:
        """
        Rebuild entire vector index from scratch
        Useful after model changes or corruption

        Args:
            entries: All entries to index

        Returns:
            Number of indexed entries
        """
        logger.info("Rebuilding vector index...")

        # Clear existing collection
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )

        # Re-index all entries
        count = self.add_entries_batch(entries)

        logger.info(f"Vector index rebuilt with {count} entries")
        return count

    def _prepare_text(self, entry: Entry) -> str:
        """
        Prepare entry text for embedding
        Combines title, content, and metadata

        Args:
            entry: Entry object

        Returns:
            Formatted text for embedding
        """
        # Weight title more heavily by including it multiple times
        text_parts = [entry.title, entry.title, entry.content]  # Title twice for emphasis

        # Add tags as keywords
        if entry.tags:
            tags_text = " ".join([f"#{tag.name}" for tag in entry.tags])
            text_parts.append(tags_text)

        # Add projects
        if entry.projects:
            projects_text = " ".join([f"@{proj.name}" for proj in entry.projects])
            text_parts.append(projects_text)

        # Combine with spaces
        full_text = " ".join(text_parts)

        # Truncate if too long (models have token limits)
        # Most sentence transformers have 512 token limit
        max_chars = 5000  # Conservative limit
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars]

        return full_text

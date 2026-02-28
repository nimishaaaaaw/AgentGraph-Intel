"""
Vector store — ChromaDB-backed persistent collection for document chunks.

Compatible with chromadb==0.4.22.
"""
from typing import List, Dict, Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

_COLLECTION_NAME = "agentgraph_docs"


class VectorStore:
    """Manages the ChromaDB collection used for semantic retrieval."""

    _client = None
    _collection = None

    def __init__(self) -> None:
        self._ensure_initialized()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_documents(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """
        Upsert document chunks into the collection.
        Using *upsert* semantics so re-ingesting a document is idempotent.
        """
        if not chunk_ids:
            return
        self._collection.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info("Upserted %d chunks into vector store", len(chunk_ids))

    def similarity_search(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the top-k most similar chunks.

        Returns a list of dicts with keys: id, content, metadata, distance.
        """
        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self._collection.query(**kwargs)

        output: List[Dict[str, Any]] = []
        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for cid, doc, meta, dist in zip(ids, docs, metas, distances):
            output.append(
                {
                    "id": cid,
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    # Convert Chroma L2 distance to a rough similarity score
                    "score": max(0.0, 1.0 - dist),
                }
            )
        return output

    def delete_by_doc_id(self, doc_id: str) -> None:
        """Delete all chunks belonging to the given document ID."""
        try:
            self._collection.delete(where={"doc_id": doc_id})
            logger.info("Deleted chunks for doc_id=%s", doc_id)
        except Exception as exc:
            logger.warning("Failed to delete doc_id=%s: %s", doc_id, exc)

    def list_documents(self) -> List[Dict[str, Any]]:
        """Return a deduplicated list of ingested documents with metadata."""
        try:
            result = self._collection.get(include=["metadatas"])
            seen: Dict[str, Dict[str, Any]] = {}
            for meta in result.get("metadatas", []):
                doc_id = meta.get("doc_id", "")
                if doc_id and doc_id not in seen:
                    seen[doc_id] = meta
            return list(seen.values())
        except Exception as exc:
            logger.error("list_documents failed: %s", exc)
            return []

    def count(self) -> int:
        """Return total number of chunks in the collection."""
        return self._collection.count()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _ensure_initialized(self) -> None:
        if VectorStore._client is not None:
            return
        import chromadb  # noqa
        from config import settings

        logger.info(
            "Initialising ChromaDB at %s", settings.chroma_persist_dir
        )
        VectorStore._client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir
        )
        VectorStore._collection = VectorStore._client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB ready — collection '%s' has %d chunks",
            _COLLECTION_NAME,
            VectorStore._collection.count(),
        )

"""
Document service — handles file ingestion, storage, and retrieval operations.
"""
import os
import tempfile
from typing import Any, Dict, List, Optional

from rag.document_processor import DocumentProcessor
from rag.embeddings import EmbeddingService
from rag.vector_store import VectorStore
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentService:
    """Orchestrate document ingestion into the RAG pipeline."""

    def __init__(self) -> None:
        self._processor = DocumentProcessor()
        self._embedder = EmbeddingService()
        self._store = VectorStore()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest_bytes(
        self,
        content: bytes,
        filename: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ingest a document from raw bytes.

        1. Write bytes to a temp file.
        2. Process (extract text, chunk).
        3. Embed chunks.
        4. Upsert into ChromaDB.

        Returns:
            ``{"doc_id": str, "chunks_created": int}``
        """
        suffix = "." + filename.rsplit(".", 1)[-1] if "." in filename else ".txt"

        with tempfile.NamedTemporaryFile(
            suffix=suffix, delete=False
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            return self._ingest_file(tmp_path, source=filename, description=description)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def ingest_file(
        self,
        file_path: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ingest a document from a filesystem path."""
        return self._ingest_file(file_path, source=file_path, description=description)

    def list_documents(self) -> List[Dict[str, Any]]:
        """Return metadata for all ingested documents."""
        return self._store.list_documents()

    def delete_document(self, doc_id: str) -> None:
        """Remove all chunks belonging to *doc_id* from the vector store."""
        self._store.delete_by_doc_id(doc_id)

    def get_chunks(self, doc_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Return stored chunks for a document (debugging aid)."""
        try:
            import chromadb  # noqa

            # Use similarity_search with a neutral query to fetch by doc_id
            results = self._store.similarity_search(
                query_embedding=[0.0] * 384,  # zero vector — distance irrelevant
                n_results=limit,
                where={"doc_id": doc_id},
            )
            return [
                {"chunk_id": r["id"], "content": r["content"], "metadata": r["metadata"]}
                for r in results
            ]
        except Exception as exc:
            logger.warning("get_chunks failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ingest_file(
        self,
        file_path: str,
        source: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        chunks = self._processor.process_file(file_path)
        if not chunks:
            logger.warning("No chunks produced from '%s'", source)
            return {"doc_id": "", "chunks_created": 0}

        doc_id = chunks[0].doc_id
        texts = [c.content for c in chunks]
        embeddings = self._embedder.embed_texts(texts)

        metadatas = []
        for c in chunks:
            meta = dict(c.metadata)
            meta["filename"] = source
            meta["source"] = source
            if description:
                meta["description"] = description
            metadatas.append(meta)

        self._store.add_documents(
            chunk_ids=[c.chunk_id for c in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        logger.info(
            "Ingested '%s' → doc_id=%s, %d chunks", source, doc_id, len(chunks)
        )
        return {"doc_id": doc_id, "chunks_created": len(chunks)}

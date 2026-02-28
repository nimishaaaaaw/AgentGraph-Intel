"""
Hybrid retriever — combines dense (ChromaDB) and sparse (BM25) retrieval
using Reciprocal Rank Fusion (RRF) for score normalisation.
"""
from typing import List, Dict, Any, Optional

from rag.embeddings import EmbeddingService
from rag.vector_store import VectorStore
from utils.logger import get_logger

logger = get_logger(__name__)

# RRF constant — controls how fast the denominator grows
_RRF_K = 60


def _reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
) -> List[Dict[str, Any]]:
    """
    Merge two ranked lists using Reciprocal Rank Fusion.

    Each result must have an ``id`` key.  The fused score is:
        rrf_score = dense_weight / (k + dense_rank) + sparse_weight / (k + sparse_rank)
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    for rank, item in enumerate(dense_results):
        cid = item["id"]
        scores[cid] = scores.get(cid, 0.0) + dense_weight / (_RRF_K + rank + 1)
        doc_map[cid] = item

    for rank, item in enumerate(sparse_results):
        cid = item["id"]
        scores[cid] = scores.get(cid, 0.0) + sparse_weight / (_RRF_K + rank + 1)
        if cid not in doc_map:
            doc_map[cid] = item

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for cid, score in fused:
        entry = dict(doc_map[cid])
        entry["score"] = round(score, 6)
        results.append(entry)
    return results


class HybridRetriever:
    """
    Two-stage hybrid retriever.

    Stage 1 — Dense retrieval via ChromaDB (semantic similarity).
    Stage 2 — Sparse retrieval via BM25 over the dense candidate set.
    Stage 3 — RRF fusion and optional top-k truncation.
    """

    def __init__(
        self,
        dense_top_k: int = 20,
        sparse_top_k: int = 20,
        final_top_k: int = 10,
    ) -> None:
        self.dense_top_k = dense_top_k
        self.sparse_top_k = sparse_top_k
        self.final_top_k = final_top_k
        self._embedder = EmbeddingService()
        self._store = VectorStore()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        filter_doc_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and fuse results for the given query.

        Args:
            query: The user query string.
            filter_doc_id: If provided, restrict search to a single document.

        Returns:
            List of result dicts sorted by fused score (descending).
        """
        # Dense retrieval
        query_embedding = self._embedder.embed_query(query)
        where = {"doc_id": filter_doc_id} if filter_doc_id else None
        dense_results = self._store.similarity_search(
            query_embedding, n_results=self.dense_top_k, where=where
        )

        if not dense_results:
            logger.info("No dense results for query: %s", query[:80])
            return []

        # Sparse retrieval over the dense candidate pool
        sparse_results = self._bm25_retrieve(
            query, dense_results, top_k=self.sparse_top_k
        )

        # Fuse
        fused = _reciprocal_rank_fusion(dense_results, sparse_results)
        top_results = fused[: self.final_top_k]

        logger.info(
            "Hybrid retrieval: dense=%d sparse=%d fused=%d returned=%d",
            len(dense_results),
            len(sparse_results),
            len(fused),
            len(top_results),
        )
        return top_results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _bm25_retrieve(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Run BM25 scoring over a candidate list."""
        try:
            from rank_bm25 import BM25Okapi  # noqa

            corpus = [item["content"].split() for item in candidates]
            bm25 = BM25Okapi(corpus)
            query_tokens = query.split()
            scores = bm25.get_scores(query_tokens)

            ranked = sorted(
                zip(scores, candidates), key=lambda x: x[0], reverse=True
            )
            results = []
            for score, item in ranked[:top_k]:
                entry = dict(item)
                entry["bm25_score"] = float(score)
                results.append(entry)
            return results

        except Exception as exc:
            logger.warning("BM25 retrieval failed: %s", exc)
            return candidates[:top_k]

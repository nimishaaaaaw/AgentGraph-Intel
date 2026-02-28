"""
Cross-encoder reranker.

After hybrid retrieval a light cross-encoder model rescores each
(query, chunk) pair to produce a more accurate relevance ordering.
Uses the ``cross-encoder/ms-marco-MiniLM-L-6-v2`` model by default.
"""
from typing import List, Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    """Thin wrapper around a sentence-transformers CrossEncoder."""

    _model = None
    _model_name: str = _DEFAULT_MODEL

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Rescore *candidates* against *query* and return the top-k results.

        Each candidate dict must contain a ``content`` key.

        Returns:
            List of candidate dicts (subset of input) sorted by
            cross-encoder score descending, with a ``rerank_score`` key added.
        """
        if not candidates:
            return []

        try:
            model = self._get_model()
            pairs = [[query, item["content"]] for item in candidates]
            scores = model.predict(pairs, show_progress_bar=False)

            scored = sorted(
                zip(scores.tolist(), candidates),
                key=lambda x: x[0],
                reverse=True,
            )
            results = []
            for score, item in scored[:top_k]:
                entry = dict(item)
                entry["rerank_score"] = round(float(score), 6)
                results.append(entry)

            logger.info(
                "Reranked %d → %d candidates", len(candidates), len(results)
            )
            return results

        except Exception as exc:
            logger.warning(
                "Reranker unavailable (%s) — returning top-%d unranked", exc, top_k
            )
            return candidates[:top_k]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_model(self):
        if Reranker._model is None:
            from sentence_transformers import CrossEncoder  # noqa

            logger.info("Loading CrossEncoder model: %s", self._model_name)
            Reranker._model = CrossEncoder(self._model_name)
            logger.info("CrossEncoder model loaded")
        return Reranker._model

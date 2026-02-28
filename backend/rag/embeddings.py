"""
Embedding service — wraps sentence-transformers for local dense embeddings.

The model is loaded once and reused across all requests to avoid the
expensive initialisation overhead.
"""
from typing import List

from utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_MODEL = "all-MiniLM-L6-v2"
_BATCH_SIZE = 64


class EmbeddingService:
    """Thin wrapper around a SentenceTransformer model."""

    _instance = None  # module-level singleton

    def __new__(cls, model_name: str = _DEFAULT_MODEL):
        # Simple singleton — one model per process
        if cls._instance is None:
            obj = super().__new__(cls)
            obj._model_name = model_name
            obj._model = None
            cls._instance = obj
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Return a list of embedding vectors for the given texts."""
        if not texts:
            return []
        model = self._get_model()
        embeddings = model.encode(
            texts,
            batch_size=_BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string."""
        return self.embed_texts([query])[0]

    @property
    def dimension(self) -> int:
        """Return the embedding dimension of the loaded model."""
        model = self._get_model()
        return model.get_sentence_embedding_dimension()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # noqa

            logger.info("Loading SentenceTransformer model: %s", self._model_name)
            self._model = SentenceTransformer(self._model_name)
            logger.info(
                "Model loaded — embedding dimension: %d",
                self._model.get_sentence_embedding_dimension(),
            )
        return self._model

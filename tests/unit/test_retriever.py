"""
Unit tests for the HybridRetriever.
"""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_chunk(chunk_id: str, content: str, score: float = 0.9):
    return {
        "id": chunk_id,
        "content": content,
        "metadata": {"source": "test.pdf", "filename": "test.pdf", "doc_id": "doc1"},
        "score": score,
        "distance": 1 - score,
    }


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.similarity_search.return_value = [
        _make_chunk("c1", "LangGraph enables multi-agent workflows.", 0.95),
        _make_chunk("c2", "Neo4j is a graph database by Neo4j Inc.", 0.87),
        _make_chunk("c3", "ChromaDB is an AI-native vector database.", 0.80),
    ]
    return store


@pytest.fixture
def mock_embedder():
    emb = MagicMock()
    emb.embed_query.return_value = [0.1] * 384
    return emb


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHybridRetriever:
    def test_retrieve_returns_fused_results(self, mock_store, mock_embedder):
        with (
            patch("rag.retriever.VectorStore", return_value=mock_store),
            patch("rag.retriever.EmbeddingService", return_value=mock_embedder),
        ):
            from rag.retriever import HybridRetriever

            retriever = HybridRetriever(dense_top_k=5, sparse_top_k=5, final_top_k=3)
            results = retriever.retrieve("What is LangGraph?")

        assert isinstance(results, list)
        assert len(results) <= 3
        # All results must have expected keys
        for r in results:
            assert "id" in r
            assert "content" in r
            assert "score" in r

    def test_retrieve_returns_empty_on_no_dense_results(
        self, mock_store, mock_embedder
    ):
        mock_store.similarity_search.return_value = []
        with (
            patch("rag.retriever.VectorStore", return_value=mock_store),
            patch("rag.retriever.EmbeddingService", return_value=mock_embedder),
        ):
            from rag.retriever import HybridRetriever

            retriever = HybridRetriever()
            results = retriever.retrieve("What is Neo4j?")

        assert results == []

    def test_reciprocal_rank_fusion_merges_and_scores(self):
        from rag.retriever import _reciprocal_rank_fusion

        dense = [
            {"id": "a", "content": "doc a", "score": 0.9},
            {"id": "b", "content": "doc b", "score": 0.8},
        ]
        sparse = [
            {"id": "b", "content": "doc b", "score": 0.7},
            {"id": "c", "content": "doc c", "score": 0.6},
        ]
        fused = _reciprocal_rank_fusion(dense, sparse)

        ids = [r["id"] for r in fused]
        assert "a" in ids
        assert "b" in ids
        assert "c" in ids
        # 'b' appears in both lists so it should rank highest
        assert fused[0]["id"] == "b"

    def test_retrieve_with_doc_id_filter(self, mock_store, mock_embedder):
        with (
            patch("rag.retriever.VectorStore", return_value=mock_store),
            patch("rag.retriever.EmbeddingService", return_value=mock_embedder),
        ):
            from rag.retriever import HybridRetriever

            retriever = HybridRetriever()
            retriever.retrieve("test query", filter_doc_id="doc1")

        # Ensure the store was called with a where clause
        call_kwargs = mock_store.similarity_search.call_args[1]
        assert call_kwargs.get("where") == {"doc_id": "doc1"}

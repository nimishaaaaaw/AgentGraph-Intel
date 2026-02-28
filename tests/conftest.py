"""
Pytest configuration and shared fixtures for AgentGraph Intel tests.
"""
import sys
import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Ensure backend is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


# ---------------------------------------------------------------------------
# LLM mock fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_llm():
    """Return a mock LLM that always returns a canned response."""
    llm = MagicMock()
    llm.generate.return_value = "This is a mock LLM response."
    llm.is_available.return_value = True
    return llm


@pytest.fixture
def patch_llm(mock_llm):
    """Patch LLMFactory.get_llm for the duration of the test."""
    with patch("llm.llm_factory.LLMFactory.get_llm", return_value=mock_llm):
        yield mock_llm


# ---------------------------------------------------------------------------
# Vector store mock fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_vector_store():
    """Return a mock VectorStore."""
    store = MagicMock()
    store.similarity_search.return_value = [
        {
            "id": "chunk-001",
            "content": "LangGraph is a library for building stateful multi-agent applications.",
            "metadata": {"source": "test.pdf", "filename": "test.pdf", "doc_id": "abc123"},
            "score": 0.92,
            "distance": 0.08,
        }
    ]
    store.count.return_value = 42
    store.list_documents.return_value = [
        {"doc_id": "abc123", "filename": "test.pdf", "source": "test.pdf"}
    ]
    return store


# ---------------------------------------------------------------------------
# Neo4j mock fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_neo4j():
    """Return a mock Neo4jClient."""
    client = MagicMock()
    client.health_check.return_value = True
    client.run_query.return_value = [{"name": "LangGraph", "type": "TECHNOLOGY"}]
    client.run_write_query.return_value = []
    return client


# ---------------------------------------------------------------------------
# Sample document fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_text() -> str:
    return (
        "LangGraph is an open-source library developed by LangChain Inc. "
        "It enables developers to build stateful, multi-actor applications "
        "with large language models. Neo4j is a leading graph database. "
        "Google DeepMind published AlphaFold, a landmark AI system for "
        "protein structure prediction."
    )

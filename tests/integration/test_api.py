"""
Integration tests for the FastAPI endpoints.
Uses TestClient with all heavyweight dependencies mocked.
"""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
    """Build a TestClient with all external dependencies mocked at module level."""
    mock_state = {
        "final_answer": "LangGraph is a multi-agent framework.",
        "sources": [{"content": "test", "source": "doc.pdf", "score": 0.9}],
        "steps_taken": ["router:researcher", "researcher", "synthesiser"],
        "error": None,
    }

    with (
        patch("agents.orchestrator.run_agent", return_value=mock_state),
        patch(
            "rag.vector_store.VectorStore._ensure_initialized"
        ),
        patch(
            "knowledge_graph.neo4j_client.Neo4jClient._ensure_connected"
        ),
        patch("llm.llm_factory.LLMFactory.get_llm", return_value=MagicMock(
            generate=MagicMock(return_value="mock"),
            is_available=MagicMock(return_value=True),
        )),
    ):
        from main import app

        yield TestClient(app)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------


class TestRootEndpoint:
    def test_root_returns_app_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------


class TestHealthEndpoints:
    def test_health_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_detailed_health_returns_services(self, client):
        with (
            patch("rag.vector_store.VectorStore.count", return_value=10),
            patch(
                "knowledge_graph.neo4j_client.Neo4jClient.health_check",
                return_value=True,
            ),
        ):
            response = client.get("/api/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data


# ---------------------------------------------------------------------------
# Chat endpoints
# ---------------------------------------------------------------------------


class TestChatEndpoints:
    def test_chat_returns_answer(self, client):
        payload = {"message": "What is LangGraph?", "session_id": "test-session"}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"] != ""

    def test_chat_requires_message(self, client):
        response = client.post("/api/chat", json={"session_id": "x"})
        assert response.status_code == 422  # validation error

    def test_chat_stream_returns_events(self, client):
        payload = {"message": "Explain RAG", "session_id": "stream-test"}
        response = client.post("/api/chat/stream", json=payload)
        assert response.status_code == 200
        # Content-type should be SSE
        assert "text/event-stream" in response.headers.get("content-type", "")

    def test_get_history_endpoint(self, client):
        response = client.get("/api/chat/history/test-session")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data

    def test_clear_history_endpoint(self, client):
        response = client.delete("/api/chat/history/test-session")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Document endpoints
# ---------------------------------------------------------------------------


class TestDocumentEndpoints:
    def test_list_documents_returns_list(self, client):
        with patch(
            "services.document_service.DocumentService.list_documents",
            return_value=[],
        ):
            response = client.get("/api/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_upload_document_txt(self, client):
        with patch(
            "services.document_service.DocumentService.ingest_bytes",
            return_value={"doc_id": "abc123", "chunks_created": 5},
        ):
            response = client.post(
                "/api/documents/upload",
                files={"file": ("test.txt", b"Hello world content", "text/plain")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["chunks_created"] == 5

    def test_upload_rejects_unsupported_type(self, client):
        response = client.post(
            "/api/documents/upload",
            files={"file": ("test.exe", b"binary", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_delete_document(self, client):
        with patch(
            "services.document_service.DocumentService.delete_document"
        ):
            response = client.delete("/api/documents/abc123")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Graph endpoints
# ---------------------------------------------------------------------------


class TestGraphEndpoints:
    def test_get_entities(self, client):
        with patch(
            "services.graph_service.GraphService.get_entities",
            return_value=[{"name": "Neo4j", "type": "TECHNOLOGY", "description": ""}],
        ):
            response = client.get("/api/graph/entities")
        assert response.status_code == 200

    def test_get_relationships(self, client):
        with patch(
            "services.graph_service.GraphService.get_relationships",
            return_value=[],
        ):
            response = client.get("/api/graph/relationships")
        assert response.status_code == 200

    def test_search_graph(self, client):
        with patch(
            "services.graph_service.GraphService.search_entities",
            return_value=[],
        ):
            response = client.get("/api/graph/search?q=neo4j")
        assert response.status_code == 200

    def test_get_graph_stats(self, client):
        with patch(
            "services.graph_service.GraphService.get_stats",
            return_value={"available": True, "total_entities": 5, "total_relationships": 3},
        ):
            response = client.get("/api/graph/stats")
        assert response.status_code == 200

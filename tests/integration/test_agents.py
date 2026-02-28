"""
Integration tests for the agent orchestrator and individual agents.
All external dependencies (LLM, vector store, Neo4j) are mocked.
"""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

_MOCK_RAG_RESULT = {
    "answer": "LangGraph is a library for building stateful multi-agent applications.",
    "sources": [
        {
            "content": "LangGraph enables multi-agent workflows.",
            "source": "test.pdf",
            "filename": "test.pdf",
            "score": 0.95,
        }
    ],
}


@pytest.fixture(autouse=True)
def patch_query_engine():
    """Patch QueryEngine so no real embeddings or ChromaDB calls are made."""
    mock_engine = MagicMock()
    mock_engine.query.return_value = _MOCK_RAG_RESULT
    with patch("rag.query_engine.QueryEngine", return_value=mock_engine):
        yield mock_engine


@pytest.fixture(autouse=True)
def patch_llm_factory():
    """Patch LLMFactory so no real LLM calls are made."""
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Synthesised mock answer."
    mock_llm.is_available.return_value = True
    with patch("llm.llm_factory.LLMFactory.get_llm", return_value=mock_llm):
        yield mock_llm


# ---------------------------------------------------------------------------
# Router tests
# ---------------------------------------------------------------------------


class TestRouter:
    def test_routes_to_researcher_by_default(self):
        from agents.router import route_query

        state = {
            "query": "What is machine learning?",
            "session_id": "test",
            "steps_taken": [],
        }
        result = route_query(state)
        assert result["route"] == "researcher"

    def test_routes_to_kg_builder_on_keywords(self):
        from agents.router import route_query

        state = {
            "query": "Extract entities and build knowledge graph from this text.",
            "session_id": "test",
            "steps_taken": [],
        }
        result = route_query(state)
        assert result["route"] == "kg_builder"

    def test_routes_to_analyst_on_keywords(self):
        from agents.router import route_query

        state = {
            "query": "Compare LangGraph and AutoGen frameworks.",
            "session_id": "test",
            "steps_taken": [],
        }
        result = route_query(state)
        assert result["route"] == "analyst"

    def test_steps_taken_updated(self):
        from agents.router import route_query

        state = {
            "query": "Tell me about Neo4j.",
            "session_id": "test",
            "steps_taken": ["prior_step"],
        }
        result = route_query(state)
        assert len(result["steps_taken"]) == 2
        assert result["steps_taken"][0] == "prior_step"


# ---------------------------------------------------------------------------
# Researcher agent tests
# ---------------------------------------------------------------------------


class TestResearcherAgent:
    def test_returns_rag_results(self, patch_query_engine):
        from agents.researcher_agent import researcher_agent

        state = {
            "query": "What is LangGraph?",
            "session_id": "test",
            "steps_taken": [],
            "route": "researcher",
        }
        result = researcher_agent(state)

        assert result["rag_answer"] != ""
        assert isinstance(result["retrieved_docs"], list)
        assert "researcher" in result["steps_taken"]

    def test_handles_query_engine_failure_gracefully(self):
        from agents.researcher_agent import researcher_agent

        with patch(
            "agents.researcher_agent.QueryEngine",
            side_effect=RuntimeError("engine down"),
        ):
            state = {
                "query": "test query",
                "session_id": "test",
                "steps_taken": [],
            }
            result = researcher_agent(state)

        assert result["error"] is not None
        assert "researcher:error" in result["steps_taken"]


# ---------------------------------------------------------------------------
# Orchestrator integration test
# ---------------------------------------------------------------------------


class TestOrchestrator:
    def test_run_agent_returns_final_answer(self):
        """End-to-end: run_agent should return a non-empty final_answer."""
        with patch(
            "knowledge_graph.entity_extractor.LLMFactory.get_llm"
        ), patch(
            "knowledge_graph.relationship_builder.LLMFactory.get_llm"
        ), patch(
            "knowledge_graph.neo4j_client.Neo4jClient"
        ):
            from agents.orchestrator import run_agent

            # Reset singleton so graph is rebuilt with mocks in place
            import agents.orchestrator as orch_module

            orch_module._graph = None

            state = run_agent("What is LangGraph?", session_id="integration-test")

        assert isinstance(state, dict)
        assert "final_answer" in state
        assert isinstance(state["steps_taken"], list)
        assert len(state["steps_taken"]) > 0

"""
Researcher agent — drives hybrid RAG retrieval and answer generation.
"""
from typing import Any, Dict

from agents.state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)


def researcher_agent(state: AgentState) -> AgentState:
    """
    Retrieve relevant document chunks via hybrid RAG and synthesise an answer.

    The agent lazily imports the query engine so that the heavy ML models are
    only loaded once the agent is actually called (not at module import time).
    """
    query = state["query"]
    logger.info("Researcher agent handling query: %s", query[:120])

    try:
        from rag.query_engine import QueryEngine  # deferred import

        engine = QueryEngine()
        result: Dict[str, Any] = engine.query(query)

        retrieved_docs = result.get("sources", [])
        rag_answer = result.get("answer", "")

        logger.info(
            "Researcher agent retrieved %d documents", len(retrieved_docs)
        )

        return {
            **state,
            "retrieved_docs": retrieved_docs,
            "rag_answer": rag_answer,
            "steps_taken": state.get("steps_taken", []) + ["researcher"],
        }

    except Exception as exc:
        logger.exception("Researcher agent failed: %s", exc)
        return {
            **state,
            "retrieved_docs": [],
            "rag_answer": "",
            "error": str(exc),
            "steps_taken": state.get("steps_taken", []) + ["researcher:error"],
        }

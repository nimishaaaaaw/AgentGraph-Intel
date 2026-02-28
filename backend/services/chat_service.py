"""
Chat service — manages conversation sessions and delegates to the agent
orchestrator.
"""
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

# In-memory session store (replace with Redis for production)
_sessions: Dict[str, List[Dict[str, str]]] = {}


class ChatService:
    """Coordinate chat interactions with session history management."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(
        self,
        message: str,
        session_id: str = "default",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent pipeline.

        Args:
            message: The user's query.
            session_id: Conversation session identifier.
            history: Optional prior turns ``[{"role": "user"|"assistant", "content": "..."}]``.

        Returns:
            ``{"answer": str, "sources": list, "steps_taken": list}``
        """
        # Persist new user message to session
        self._append_message(session_id, "user", message)

        try:
            from agents.orchestrator import run_agent  # deferred import

            state = run_agent(query=message, session_id=session_id)
            answer = state.get("final_answer") or state.get("rag_answer") or ""
            sources = state.get("sources", [])
            steps = state.get("steps_taken", [])

        except Exception as exc:
            logger.exception("Agent pipeline error: %s", exc)
            answer = f"I encountered an error processing your request: {exc}"
            sources = []
            steps = ["error"]

        # Persist assistant response
        self._append_message(session_id, "assistant", answer)

        return {"answer": answer, "sources": sources, "steps_taken": steps}

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Return conversation history for a session."""
        return list(_sessions.get(session_id, []))

    def clear_history(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        _sessions.pop(session_id, None)
        logger.info("Cleared history for session '%s'", session_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _append_message(
        self, session_id: str, role: str, content: str
    ) -> None:
        if session_id not in _sessions:
            _sessions[session_id] = []
        _sessions[session_id].append({"role": role, "content": content})
        # Keep last 40 turns to avoid unbounded memory growth
        _sessions[session_id] = _sessions[session_id][-40:]

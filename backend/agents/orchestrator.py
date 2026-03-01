"""
LangGraph orchestrator — wires all agents into a stateful directed graph.

Compatible with langgraph>=0.2.0 (StateGraph API).
"""
from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.router import route_query, get_route
from agents.researcher_agent import researcher_agent
from agents.kg_builder_agent import kg_builder_agent
from agents.analyst_agent import analyst_agent
from agents.synthesiser import synthesiser_node
from utils.logger import get_logger

logger = get_logger(__name__)


def _build_graph() -> StateGraph:
    """Construct and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("router", route_query)
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("kg_builder", kg_builder_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("synthesiser", synthesiser_node)

    # Entry point
    workflow.set_entry_point("router")

    # Conditional routing after the router node
    workflow.add_conditional_edges(
        "router",
        get_route,
        {
            "researcher": "researcher",
            "kg_builder": "kg_builder",
            "analyst": "analyst",
        },
    )

    # All agent paths converge on the synthesiser
    workflow.add_edge("researcher", "synthesiser")
    workflow.add_edge("kg_builder", "synthesiser")
    workflow.add_edge("analyst", "synthesiser")

    # Synthesiser is the terminal node
    workflow.add_edge("synthesiser", END)

    return workflow.compile()


# Module-level compiled graph (created once per process)
_graph = None


def get_graph():
    """Return the singleton compiled workflow graph."""
    global _graph
    if _graph is None:
        logger.info("Compiling LangGraph workflow")
        _graph = _build_graph()
    return _graph


def run_agent(query: str, session_id: str = "default") -> AgentState:
    """
    Execute the agent workflow for a single query.

    Args:
        query: The user's question / instruction.
        session_id: Conversation session identifier.

    Returns:
        Final AgentState after all nodes have executed.
    """
    initial_state: AgentState = {
        "query": query,
        "session_id": session_id,
        "route": "",
        "retrieved_docs": [],
        "rag_answer": "",
        "extracted_entities": [],
        "extracted_relationships": [],
        "kg_context": "",
        "analysis": "",
        "citations": [],
        "final_answer": "",
        "sources": [],
        "error": None,
        "steps_taken": [],
    }

    graph = get_graph()
    logger.info("Running agent workflow for session=%s", session_id)
    final_state = graph.invoke(initial_state)
    logger.info(
        "Workflow complete. Steps: %s", final_state.get("steps_taken", [])
    )
    return final_state

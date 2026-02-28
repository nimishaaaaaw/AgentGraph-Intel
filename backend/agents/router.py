"""
Query router agent.
Classifies incoming queries to determine which agent pipeline to invoke.
"""
from agents.state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)

# Keywords that strongly signal knowledge-graph construction intent
_KG_KEYWORDS = frozenset(
    [
        "extract entities",
        "build graph",
        "create graph",
        "knowledge graph",
        "entities",
        "relationships",
        "map out",
        "connections between",
    ]
)

# Keywords that signal analytical/comparative reasoning
_ANALYST_KEYWORDS = frozenset(
    [
        "compare",
        "contrast",
        "analyze",
        "analyse",
        "summarize",
        "summarise",
        "evaluate",
        "assessment",
        "pros and cons",
        "difference between",
        "similarities",
    ]
)


def route_query(state: AgentState) -> AgentState:
    """
    Classify the user query and set the ``route`` field on the state.

    Routing logic (in priority order):
    1. KG-builder intent → ``kg_builder``
    2. Analytical intent  → ``analyst``
    3. Default research   → ``researcher``
    """
    query_lower = state["query"].lower()

    if any(kw in query_lower for kw in _KG_KEYWORDS):
        route = "kg_builder"
    elif any(kw in query_lower for kw in _ANALYST_KEYWORDS):
        route = "analyst"
    else:
        route = "researcher"

    logger.info("Routing query to: %s", route)
    return {
        **state,
        "route": route,
        "steps_taken": state.get("steps_taken", []) + [f"router:{route}"],
    }


def get_route(state: AgentState) -> str:
    """Return the route value for LangGraph conditional edges."""
    return state.get("route", "researcher")

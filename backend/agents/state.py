"""
Agent state definitions for LangGraph workflows.
Uses TypedDict to define the shared state passed between agent nodes.
"""
from typing import TypedDict, List, Optional, Dict, Any


class AgentState(TypedDict):
    """Shared state for the multi-agent orchestration workflow."""

    # Input fields
    query: str
    session_id: str

    # Routing
    route: str  # "researcher" | "kg_builder" | "analyst" | "direct"

    # Research agent outputs
    retrieved_docs: List[Dict[str, Any]]
    rag_answer: str

    # KG builder agent outputs
    extracted_entities: List[Dict[str, Any]]
    extracted_relationships: List[Dict[str, Any]]
    kg_context: str

    # Analyst agent outputs
    analysis: str
    citations: List[Dict[str, Any]]

    # Final output
    final_answer: str
    sources: List[Dict[str, Any]]

    # Metadata
    error: Optional[str]
    steps_taken: List[str]

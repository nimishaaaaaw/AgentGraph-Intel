"""
Final answer synthesiser node.
Merges outputs from all preceding agents into a single coherent response
and builds the ``sources`` list for citation rendering.
"""
from agents.state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)

_FINAL_PROMPT = """Based on the research and analysis below, provide a clear and comprehensive answer to the user's question.

Question: {query}

Research Findings: {rag_answer}

Analysis: {analysis}

Knowledge Graph Insights: {kg_context}

Provide a well-structured, accurate answer with appropriate citations where relevant.

Answer:"""


def synthesiser_node(state: AgentState) -> AgentState:
    """Combine all agent outputs into a final answer."""
    query = state["query"]
    rag_answer = state.get("rag_answer", "")
    analysis = state.get("analysis", "")
    kg_context = state.get("kg_context", "")

    # Prefer the richest available answer
    if analysis:
        candidate = analysis
    elif rag_answer:
        candidate = rag_answer
    else:
        candidate = "I could not find sufficient information to answer your question."

    # If we have multiple sources of information, synthesise with LLM
    if rag_answer and analysis:
        try:
            from llm.llm_factory import LLMFactory

            llm = LLMFactory.get_llm()
            prompt = _FINAL_PROMPT.format(
                query=query,
                rag_answer=rag_answer[:1500],
                analysis=analysis[:1500],
                kg_context=kg_context[:500] if kg_context else "None",
            )
            candidate = llm.generate(prompt)
        except Exception as exc:
            logger.warning("Final synthesis LLM call failed: %s", exc)

    # Build unified sources list
    sources = []
    for doc in state.get("retrieved_docs", []):
        sources.append(
            {
                "content": doc.get("content", "")[:300],
                "source": doc.get("source", "unknown"),
                "score": doc.get("score", 0.0),
            }
        )

    logger.info("Synthesiser produced final answer (%d chars)", len(candidate))

    return {
        **state,
        "final_answer": candidate,
        "sources": sources,
        "steps_taken": state.get("steps_taken", []) + ["synthesiser"],
    }

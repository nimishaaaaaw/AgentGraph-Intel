"""
Analyst agent.
Synthesises a structured analysis from RAG results, KG context, and the
raw query using the configured LLM.
"""
from agents.state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)

_ANALYSIS_PROMPT_TEMPLATE = """You are an expert research analyst. Based on the following information, provide a comprehensive analysis.

User Query: {query}

Retrieved Documents:
{docs_text}

Knowledge Graph Context:
{kg_context}

Initial RAG Answer:
{rag_answer}

Please provide:
1. A thorough analysis addressing the query
2. Key insights and patterns identified
3. Supporting evidence from the sources
4. Any limitations or caveats

Analysis:"""


def analyst_agent(state: AgentState) -> AgentState:
    """
    Produce a structured analytical response by combining:
    - Hybrid RAG results (if not already populated)
    - Knowledge graph context
    - LLM reasoning
    """
    query = state["query"]
    logger.info("Analyst agent handling query: %s", query[:120])

    try:
        # If researcher hasn't run yet, do retrieval now
        retrieved_docs = state.get("retrieved_docs") or []
        rag_answer = state.get("rag_answer", "")

        if not retrieved_docs:
            from rag.query_engine import QueryEngine

            engine = QueryEngine()
            rag_result = engine.query(query)
            retrieved_docs = rag_result.get("sources", [])
            rag_answer = rag_result.get("answer", "")

        kg_context = state.get("kg_context", "No knowledge graph context available.")

        # Build prompt context
        docs_text = "\n\n".join(
            f"[Source {i + 1}] {doc.get('content', '')[:600]}"
            for i, doc in enumerate(retrieved_docs[:5])
        )

        prompt = _ANALYSIS_PROMPT_TEMPLATE.format(
            query=query,
            docs_text=docs_text or "No documents retrieved.",
            kg_context=kg_context,
            rag_answer=rag_answer or "No initial answer.",
        )

        from llm.llm_factory import LLMFactory

        llm = LLMFactory.get_llm()
        analysis = llm.generate(prompt)

        # Build citations list
        citations = [
            {
                "index": i + 1,
                "source": doc.get("source", "unknown"),
                "score": doc.get("score", 0.0),
            }
            for i, doc in enumerate(retrieved_docs[:5])
        ]

        logger.info("Analyst agent produced analysis (%d chars)", len(analysis))

        return {
            **state,
            "retrieved_docs": retrieved_docs,
            "rag_answer": rag_answer,
            "analysis": analysis,
            "citations": citations,
            "steps_taken": state.get("steps_taken", []) + ["analyst"],
        }

    except Exception as exc:
        logger.exception("Analyst agent failed: %s", exc)
        return {
            **state,
            "analysis": "",
            "citations": [],
            "error": str(exc),
            "steps_taken": state.get("steps_taken", []) + ["analyst:error"],
        }

"""
RAG query engine — orchestrates retrieval, reranking, and generation.
"""
from typing import Dict, Any, List, Optional

from rag.retriever import HybridRetriever
from rag.reranker import Reranker
from utils.logger import get_logger

logger = get_logger(__name__)

_ANSWER_PROMPT = """You are a knowledgeable research assistant. Answer the question based *only* on the provided context. If the context does not contain enough information, say so clearly.

Question: {question}

Context:
{context}

Answer:"""


class QueryEngine:
    """
    End-to-end RAG pipeline:
    1. Hybrid retrieval (dense + sparse)
    2. Cross-encoder reranking
    3. LLM answer generation
    """

    def __init__(
        self,
        retriever_top_k: int = 10,
        rerank_top_k: int = 5,
    ) -> None:
        self._retriever = HybridRetriever(final_top_k=retriever_top_k)
        self._reranker = Reranker()
        self._rerank_top_k = rerank_top_k

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(
        self,
        question: str,
        filter_doc_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the full RAG pipeline for a question.

        Returns:
            {
                "answer": str,
                "sources": List[Dict],
            }
        """
        # Step 1 — retrieve
        candidates = self._retriever.retrieve(question, filter_doc_id=filter_doc_id)
        if not candidates:
            return {
                "answer": "I could not find relevant information to answer your question.",
                "sources": [],
            }

        # Step 2 — rerank
        ranked = self._reranker.rerank(question, candidates, top_k=self._rerank_top_k)

        # Step 3 — build context and generate
        context = self._build_context(ranked)
        answer = self._generate(question, context)

        # Normalise source metadata for the API response
        sources = [
            {
                "content": item.get("content", "")[:400],
                "source": item.get("metadata", {}).get("source", "unknown"),
                "filename": item.get("metadata", {}).get("filename", ""),
                "score": item.get("rerank_score", item.get("score", 0.0)),
            }
            for item in ranked
        ]

        return {"answer": answer, "sources": sources}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_context(self, ranked: List[Dict[str, Any]]) -> str:
        parts = []
        for i, item in enumerate(ranked, 1):
            source = item.get("metadata", {}).get("filename", "unknown")
            parts.append(f"[{i}] (source: {source})\n{item.get('content', '')}")
        return "\n\n---\n\n".join(parts)

    def _generate(self, question: str, context: str) -> str:
        try:
            from llm.llm_factory import LLMFactory

            llm = LLMFactory.get_llm()
            prompt = _ANSWER_PROMPT.format(question=question, context=context)
            return llm.generate(prompt)
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            return f"Retrieved context was found but answer generation failed: {exc}"

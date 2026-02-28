"""
Knowledge-Graph builder agent.
Extracts entities and relationships from retrieved documents and persists
them to Neo4j, then fetches graph-based context to enrich the answer.
"""
from agents.state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)


def kg_builder_agent(state: AgentState) -> AgentState:
    """
    1. Run hybrid RAG retrieval (same as researcher).
    2. Extract named entities and relationships from the chunks.
    3. Persist entities/relationships to Neo4j.
    4. Query the graph for contextual neighbours.
    5. Return enriched state.
    """
    query = state["query"]
    logger.info("KG builder agent handling query: %s", query[:120])

    try:
        from rag.query_engine import QueryEngine
        from knowledge_graph.entity_extractor import EntityExtractor
        from knowledge_graph.relationship_builder import RelationshipBuilder
        from knowledge_graph.graph_rag import GraphRAG

        # Step 1 – retrieve docs
        engine = QueryEngine()
        rag_result = engine.query(query)
        retrieved_docs = rag_result.get("sources", [])
        rag_answer = rag_result.get("answer", "")

        # Step 2 – extract entities & relationships from chunk text
        combined_text = " ".join(
            doc.get("content", "") for doc in retrieved_docs
        )
        extractor = EntityExtractor()
        entities = extractor.extract(combined_text)

        builder = RelationshipBuilder()
        relationships = builder.build(combined_text, entities)

        # Step 3 – persist to Neo4j (best-effort; failures are non-fatal)
        try:
            builder.persist(entities, relationships)
        except Exception as persist_err:
            logger.warning("KG persist failed (non-fatal): %s", persist_err)

        # Step 4 – graph-augmented context
        graph_rag = GraphRAG()
        kg_context = graph_rag.get_context(query, entities)

        logger.info(
            "KG builder extracted %d entities, %d relationships",
            len(entities),
            len(relationships),
        )

        return {
            **state,
            "retrieved_docs": retrieved_docs,
            "rag_answer": rag_answer,
            "extracted_entities": entities,
            "extracted_relationships": relationships,
            "kg_context": kg_context,
            "steps_taken": state.get("steps_taken", []) + ["kg_builder"],
        }

    except Exception as exc:
        logger.exception("KG builder agent failed: %s", exc)
        return {
            **state,
            "extracted_entities": [],
            "extracted_relationships": [],
            "kg_context": "",
            "error": str(exc),
            "steps_taken": state.get("steps_taken", []) + ["kg_builder:error"],
        }

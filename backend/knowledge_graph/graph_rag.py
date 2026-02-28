"""
Graph-RAG — augments retrieved text chunks with structured knowledge graph context.

For a given query and set of extracted entities, this module fetches
neighbourhood information from Neo4j and formats it as additional context
for the LLM.
"""
from typing import List, Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)


class GraphRAG:
    """Retrieve and format graph context to augment LLM prompts."""

    def __init__(self) -> None:
        try:
            from knowledge_graph.neo4j_client import Neo4jClient

            self._client = Neo4jClient()
            self._available = self._client.health_check()
        except Exception as exc:
            logger.warning("GraphRAG: Neo4j unavailable — %s", exc)
            self._client = None
            self._available = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_context(
        self,
        query: str,
        entities: List[Dict[str, Any]],
        max_entities: int = 5,
    ) -> str:
        """
        Build a text summary of graph context relevant to the query.

        Args:
            query: The user's question.
            entities: Entities extracted from retrieved documents.
            max_entities: Maximum number of entities to look up in the graph.

        Returns:
            Formatted string suitable for inclusion in an LLM prompt.
        """
        if not self._available or not entities:
            return "Knowledge graph context unavailable."

        context_parts: List[str] = []

        for entity in entities[:max_entities]:
            name = entity.get("name", "")
            if not name:
                continue
            try:
                neighbours = self._get_neighbours(name)
                if neighbours:
                    context_parts.append(
                        self._format_entity_context(name, neighbours)
                    )
            except Exception as exc:
                logger.debug("Graph context fetch failed for '%s': %s", name, exc)

        if not context_parts:
            return "No relevant graph context found."

        return "Knowledge Graph Context:\n\n" + "\n\n".join(context_parts)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_neighbours(
        self, entity_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Return direct relationships for an entity."""
        query = (
            "MATCH (e:Entity {name: $name})-[r]-(neighbour:Entity) "
            "RETURN e.name AS entity, type(r) AS relation, "
            "neighbour.name AS neighbour, neighbour.type AS neighbour_type "
            "LIMIT $limit"
        )
        return self._client.run_query(
            query, {"name": entity_name, "limit": limit}
        )

    def _format_entity_context(
        self, entity_name: str, neighbours: List[Dict[str, Any]]
    ) -> str:
        lines = [f"Entity: {entity_name}"]
        for row in neighbours:
            lines.append(
                f"  └─ [{row.get('relation', 'RELATED_TO')}] → "
                f"{row.get('neighbour', '')} ({row.get('neighbour_type', '')})"
            )
        return "\n".join(lines)

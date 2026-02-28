"""
Graph service — business logic layer over the knowledge graph module.
"""
from typing import Any, Dict, List, Optional

from knowledge_graph.graph_query import GraphQuery
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphService:
    """Facade over GraphQuery providing clean, exception-safe access."""

    def __init__(self) -> None:
        self._gq = GraphQuery()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_entities(
        self,
        entity_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Return entities, optionally filtered by type."""
        try:
            return self._gq.get_entities(entity_type=entity_type, limit=limit)
        except Exception as exc:
            logger.error("get_entities error: %s", exc)
            return []

    def get_relationships(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return relationship triples."""
        try:
            return self._gq.get_relationships(limit=limit)
        except Exception as exc:
            logger.error("get_relationships error: %s", exc)
            return []

    def search_entities(
        self, search_term: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Full-text search over entity names."""
        try:
            return self._gq.search_entities(search_term, limit=limit)
        except Exception as exc:
            logger.error("search_entities error: %s", exc)
            return []

    def get_entity_neighbours(
        self, entity_name: str, max_hops: int = 2
    ) -> Dict[str, Any]:
        """Return ego-network for a given entity."""
        try:
            return self._gq.get_entity_neighbours(
                entity_name, max_hops=max_hops
            )
        except Exception as exc:
            logger.error("get_entity_neighbours error: %s", exc)
            return {"nodes": [], "edges": []}

    def get_stats(self) -> Dict[str, Any]:
        """Return knowledge graph statistics."""
        try:
            return self._gq.get_graph_stats()
        except Exception as exc:
            logger.error("get_stats error: %s", exc)
            return {"available": False, "detail": str(exc)}

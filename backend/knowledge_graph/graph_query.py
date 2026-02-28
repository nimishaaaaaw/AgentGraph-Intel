"""
Graph query module — high-level Cypher query helpers for the knowledge graph.
"""
from typing import List, Dict, Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class GraphQuery:
    """Provides named Cypher query methods over Neo4j."""

    def __init__(self) -> None:
        try:
            from knowledge_graph.neo4j_client import Neo4jClient

            self._client = Neo4jClient()
            self._available = self._client.health_check()
        except Exception as exc:
            logger.warning("GraphQuery: Neo4j unavailable — %s", exc)
            self._client = None
            self._available = False

    # ------------------------------------------------------------------
    # Entities
    # ------------------------------------------------------------------

    def get_entities(
        self,
        entity_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Return entities, optionally filtered by type."""
        if not self._available:
            return []
        query = (
            "MATCH (e:Entity) WHERE $type IS NULL OR e.type = $type "
            "RETURN e.name AS name, e.type AS type, e.description AS description "
            "LIMIT $limit"
        )
        return self._client.run_query(
            query, {"type": entity_type, "limit": limit}
        )

    def search_entities(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Full-text search over entity names (case-insensitive contains)."""
        if not self._available:
            return []
        query = (
            "MATCH (e:Entity) "
            "WHERE toLower(e.name) CONTAINS toLower($term) "
            "RETURN e.name AS name, e.type AS type, e.description AS description "
            "LIMIT $limit"
        )
        return self._client.run_query(query, {"term": search_term, "limit": limit})

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    def get_relationships(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return all relationships as (source, relationship, target) triples."""
        if not self._available:
            return []
        query = (
            "MATCH (a:Entity)-[r]->(b:Entity) "
            "RETURN a.name AS source, type(r) AS relationship, b.name AS target, "
            "r.description AS description "
            "LIMIT $limit"
        )
        return self._client.run_query(query, {"limit": limit})

    def get_entity_neighbours(
        self,
        entity_name: str,
        max_hops: int = 2,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Return the ego-network (up to *max_hops* away) for a given entity.
        """
        if not self._available:
            return {"nodes": [], "edges": []}
        query = (
            "MATCH path = (e:Entity {name: $name})-[*1..$hops]-(neighbour:Entity) "
            "WITH nodes(path) AS ns, relationships(path) AS rs "
            "UNWIND ns AS n "
            "WITH COLLECT(DISTINCT {name: n.name, type: n.type}) AS nodes, rs "
            "UNWIND rs AS r "
            "WITH nodes, COLLECT(DISTINCT { "
            "  source: startNode(r).name, "
            "  target: endNode(r).name, "
            "  relationship: type(r) "
            "}) AS edges "
            "RETURN nodes, edges "
            "LIMIT $limit"
        )
        results = self._client.run_query(
            query, {"name": entity_name, "hops": max_hops, "limit": limit}
        )
        if results:
            return results[0]
        return {"nodes": [], "edges": []}

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_graph_stats(self) -> Dict[str, Any]:
        """Return basic graph statistics."""
        if not self._available:
            return {"available": False}
        node_q = "MATCH (e:Entity) RETURN count(e) AS total_entities"
        rel_q = "MATCH ()-[r]->() RETURN count(r) AS total_relationships"
        type_q = (
            "MATCH (e:Entity) RETURN e.type AS type, count(e) AS count "
            "ORDER BY count DESC"
        )
        nodes = self._client.run_query(node_q)
        rels = self._client.run_query(rel_q)
        types = self._client.run_query(type_q)

        return {
            "available": True,
            "total_entities": nodes[0]["total_entities"] if nodes else 0,
            "total_relationships": rels[0]["total_relationships"] if rels else 0,
            "entity_types": types,
        }

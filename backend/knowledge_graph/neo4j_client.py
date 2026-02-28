"""
Neo4j client — manages driver lifecycle and provides a safe query helper.
"""
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class Neo4jClient:
    """
    Singleton Neo4j driver wrapper.

    Usage::

        client = Neo4jClient()
        results = client.run_query("MATCH (n) RETURN n LIMIT 5")
    """

    _driver = None

    def __init__(self) -> None:
        self._ensure_connected()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return all records as dicts."""
        with self._session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def run_write_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a write Cypher query inside an explicit transaction."""
        with self._session() as session:
            result = session.execute_write(
                lambda tx: list(tx.run(query, parameters or {}))
            )
            return [record.data() for record in result]

    def health_check(self) -> bool:
        """Return True if the database is reachable."""
        try:
            self.run_query("RETURN 1 AS ok")
            return True
        except Exception as exc:
            logger.warning("Neo4j health check failed: %s", exc)
            return False

    def close(self) -> None:
        """Close the driver connection."""
        if Neo4jClient._driver is not None:
            Neo4jClient._driver.close()
            Neo4jClient._driver = None
            logger.info("Neo4j driver closed")

    def create_indexes(self) -> None:
        """Create recommended indexes if they don't already exist."""
        index_queries = [
            "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX doc_id IF NOT EXISTS FOR (d:Document) ON (d.doc_id)",
        ]
        for q in index_queries:
            try:
                self.run_write_query(q)
            except Exception as exc:
                logger.debug("Index creation skipped (%s): %s", q[:40], exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_connected(self) -> None:
        if Neo4jClient._driver is not None:
            return
        try:
            from neo4j import GraphDatabase  # noqa

            logger.info("Connecting to Neo4j at %s", settings.neo4j_uri)
            Neo4jClient._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
            )
            Neo4jClient._driver.verify_connectivity()
            logger.info("Neo4j connection established")
        except Exception as exc:
            logger.warning("Neo4j connection failed: %s", exc)
            Neo4jClient._driver = None

    @contextmanager
    def _session(self):
        if Neo4jClient._driver is None:
            raise RuntimeError(
                "Neo4j driver is not connected. Check NEO4J_URI / credentials."
            )
        session = Neo4jClient._driver.session()
        try:
            yield session
        finally:
            session.close()

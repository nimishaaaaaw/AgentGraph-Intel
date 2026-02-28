"""
Unit tests for GraphQuery.
"""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.health_check.return_value = True
    client.run_query.return_value = [
        {"name": "Neo4j", "type": "TECHNOLOGY", "description": "Graph database"}
    ]
    return client


class TestGraphQuery:
    """Tests for knowledge_graph.graph_query.GraphQuery."""

    def test_get_entities_returns_list(self, mock_client):
        with patch(
            "knowledge_graph.graph_query.Neo4jClient", return_value=mock_client
        ):
            from knowledge_graph.graph_query import GraphQuery

            gq = GraphQuery()
            result = gq.get_entities()

        assert isinstance(result, list)
        assert result[0]["name"] == "Neo4j"

    def test_get_entities_with_type_filter(self, mock_client):
        with patch(
            "knowledge_graph.graph_query.Neo4jClient", return_value=mock_client
        ):
            from knowledge_graph.graph_query import GraphQuery

            gq = GraphQuery()
            gq.get_entities(entity_type="TECHNOLOGY")

        call_args = mock_client.run_query.call_args
        params = call_args[0][1]  # second positional arg is params dict
        assert params["type"] == "TECHNOLOGY"

    def test_get_entities_returns_empty_when_unavailable(self):
        with patch(
            "knowledge_graph.graph_query.Neo4jClient",
            side_effect=RuntimeError("no neo4j"),
        ):
            from knowledge_graph import graph_query
            # Force module re-evaluation
            import importlib
            importlib.reload(graph_query)
            gq = graph_query.GraphQuery()

        # _available should be False → returns []
        gq._available = False
        result = gq.get_entities()
        assert result == []

    def test_search_entities_passes_term(self, mock_client):
        with patch(
            "knowledge_graph.graph_query.Neo4jClient", return_value=mock_client
        ):
            from knowledge_graph.graph_query import GraphQuery

            gq = GraphQuery()
            gq.search_entities("langchain")

        call_args = mock_client.run_query.call_args
        params = call_args[0][1]
        assert "langchain" in params["term"]

    def test_get_graph_stats_returns_dict(self, mock_client):
        mock_client.run_query.side_effect = [
            [{"total_entities": 10}],
            [{"total_relationships": 25}],
            [{"type": "TECHNOLOGY", "count": 5}],
        ]
        with patch(
            "knowledge_graph.graph_query.Neo4jClient", return_value=mock_client
        ):
            from knowledge_graph.graph_query import GraphQuery

            gq = GraphQuery()
            stats = gq.get_graph_stats()

        assert stats["available"] is True
        assert stats["total_entities"] == 10
        assert stats["total_relationships"] == 25

    def test_get_relationships_returns_list(self, mock_client):
        mock_client.run_query.return_value = [
            {
                "source": "LangGraph",
                "relationship": "CREATED_BY",
                "target": "LangChain",
                "description": "",
            }
        ]
        with patch(
            "knowledge_graph.graph_query.Neo4jClient", return_value=mock_client
        ):
            from knowledge_graph.graph_query import GraphQuery

            gq = GraphQuery()
            rels = gq.get_relationships(limit=5)

        assert isinstance(rels, list)
        assert rels[0]["source"] == "LangGraph"

"""
Unit tests for the EntityExtractor.
"""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


class TestEntityExtractor:
    """Tests for knowledge_graph.entity_extractor.EntityExtractor."""

    def test_extract_returns_list_of_dicts(self):
        from knowledge_graph.entity_extractor import EntityExtractor

        mock_llm = MagicMock()
        mock_llm.generate.return_value = (
            '[{"name": "LangChain", "type": "ORGANIZATION", "description": "AI company"}]'
        )

        with patch(
            "knowledge_graph.entity_extractor.LLMFactory.get_llm",
            return_value=mock_llm,
        ):
            extractor = EntityExtractor()
            result = extractor.extract(
                "LangChain is a company that builds AI tools."
            )

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "LangChain"
        assert result[0]["type"] == "ORGANIZATION"

    def test_extract_empty_text_returns_empty(self):
        from knowledge_graph.entity_extractor import EntityExtractor

        extractor = EntityExtractor()
        assert extractor.extract("") == []
        assert extractor.extract("   ") == []

    def test_extract_fallback_on_llm_failure(self, sample_text):
        from knowledge_graph.entity_extractor import EntityExtractor

        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("LLM unavailable")

        with patch(
            "knowledge_graph.entity_extractor.LLMFactory.get_llm",
            return_value=mock_llm,
        ):
            extractor = EntityExtractor()
            result = extractor.extract(sample_text)

        # Fallback regex extractor should still return something
        assert isinstance(result, list)

    def test_extract_validates_entity_fields(self):
        from knowledge_graph.entity_extractor import EntityExtractor

        mock_llm = MagicMock()
        # Response includes one valid and one invalid entity
        mock_llm.generate.return_value = (
            '[{"name": "Neo4j", "type": "TECHNOLOGY", "description": "Graph DB"},'
            ' {"invalid_key": "oops"}]'
        )

        with patch(
            "knowledge_graph.entity_extractor.LLMFactory.get_llm",
            return_value=mock_llm,
        ):
            extractor = EntityExtractor()
            result = extractor.extract("Neo4j is a graph database.")

        # Only the valid entity should be returned
        assert len(result) == 1
        assert result[0]["name"] == "Neo4j"

    def test_extract_type_is_uppercased(self):
        from knowledge_graph.entity_extractor import EntityExtractor

        mock_llm = MagicMock()
        mock_llm.generate.return_value = (
            '[{"name": "Python", "type": "technology", "description": "Language"}]'
        )

        with patch(
            "knowledge_graph.entity_extractor.LLMFactory.get_llm",
            return_value=mock_llm,
        ):
            extractor = EntityExtractor()
            result = extractor.extract("Python is a programming language.")

        assert result[0]["type"] == "TECHNOLOGY"

"""
Output parsers — extract structured data from raw LLM text responses.
"""
import json
import re
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class JsonParser:
    """Extract and validate a JSON object or array from LLM output."""

    @staticmethod
    def parse(text: str) -> Any:
        """
        Attempt to parse JSON from *text*.

        Tries three strategies in order:
        1. Direct ``json.loads`` on the whole text.
        2. Regex extraction of the first JSON array.
        3. Regex extraction of the first JSON object.

        Raises:
            ValueError: If no valid JSON is found.
        """
        text = text.strip()

        # Strategy 1 — whole response is JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strategy 2 — extract first JSON array
        array_match = re.search(r"\[.*?\]", text, re.DOTALL)
        if array_match:
            try:
                return json.loads(array_match.group())
            except json.JSONDecodeError:
                pass

        # Strategy 3 — extract first JSON object
        obj_match = re.search(r"\{.*?\}", text, re.DOTALL)
        if obj_match:
            try:
                return json.loads(obj_match.group())
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not extract JSON from LLM response: {text[:200]}")


class EntityListParser:
    """Parse a list of entity dicts from LLM output."""

    REQUIRED_FIELDS = {"name", "type"}

    @classmethod
    def parse(cls, text: str) -> List[Dict[str, Any]]:
        """Return a validated list of entity dicts."""
        try:
            raw = JsonParser.parse(text)
        except ValueError as exc:
            logger.warning("EntityListParser: %s", exc)
            return []

        if not isinstance(raw, list):
            raw = [raw]

        result: List[Dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            if not cls.REQUIRED_FIELDS.issubset(item.keys()):
                continue
            result.append(
                {
                    "name": str(item["name"]).strip(),
                    "type": str(item["type"]).upper().strip(),
                    "description": str(item.get("description", "")),
                }
            )
        return result


class RelationshipListParser:
    """Parse a list of relationship dicts from LLM output."""

    REQUIRED_FIELDS = {"source", "target", "relationship"}

    @classmethod
    def parse(cls, text: str) -> List[Dict[str, Any]]:
        """Return a validated list of relationship dicts."""
        try:
            raw = JsonParser.parse(text)
        except ValueError as exc:
            logger.warning("RelationshipListParser: %s", exc)
            return []

        if not isinstance(raw, list):
            raw = [raw]

        result: List[Dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            if not cls.REQUIRED_FIELDS.issubset(item.keys()):
                continue
            result.append(
                {
                    "source": str(item["source"]).strip(),
                    "target": str(item["target"]).strip(),
                    "relationship": (
                        str(item["relationship"]).upper().replace(" ", "_").strip()
                    ),
                    "description": str(item.get("description", "")),
                }
            )
        return result


class AnswerWithCitationsParser:
    """
    Parse an answer that may contain inline citation markers like [1], [2, 3].

    Returns:
        {
            "answer": str,            # cleaned answer text
            "citation_indices": list  # e.g. [1, 2, 3]
        }
    """

    @staticmethod
    def parse(text: str) -> Dict[str, Any]:
        citation_pattern = re.compile(r"\[(\d+(?:,\s*\d+)*)\]")
        indices: List[int] = []
        for match in citation_pattern.finditer(text):
            for num_str in match.group(1).split(","):
                try:
                    indices.append(int(num_str.strip()))
                except ValueError:
                    pass
        return {
            "answer": text.strip(),
            "citation_indices": sorted(set(indices)),
        }

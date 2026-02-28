"""
Entity extractor — uses an LLM prompt to extract named entities from text.

Falls back to a simple regex-based heuristic when the LLM is unavailable.
"""
import json
import re
from typing import List, Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)

_ENTITY_TYPES = [
    "PERSON", "ORGANIZATION", "LOCATION", "TECHNOLOGY",
    "CONCEPT", "EVENT", "PRODUCT", "DATE",
]

_EXTRACT_PROMPT = """Extract named entities from the following text. For each entity provide:
- name: the entity name as it appears in the text
- type: one of {types}
- description: a brief description (1 sentence max)

Return ONLY a JSON array of objects. No explanation.

Text:
{text}

JSON:"""


class EntityExtractor:
    """Extract named entities from document text."""

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from *text*.

        Returns:
            List of entity dicts: ``{"name": str, "type": str, "description": str}``
        """
        if not text or not text.strip():
            return []

        # Truncate to keep prompt size manageable
        snippet = text[:3000]

        try:
            return self._llm_extract(snippet)
        except Exception as exc:
            logger.warning("LLM entity extraction failed (%s); using fallback", exc)
            return self._regex_extract(snippet)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _llm_extract(self, text: str) -> List[Dict[str, Any]]:
        from llm.llm_factory import LLMFactory  # deferred

        llm = LLMFactory.get_llm()
        prompt = _EXTRACT_PROMPT.format(
            types=", ".join(_ENTITY_TYPES), text=text
        )
        raw = llm.generate(prompt)

        # Extract the JSON array from the response
        json_match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON array found in LLM response")

        entities = json.loads(json_match.group())
        validated: List[Dict[str, Any]] = []
        for ent in entities:
            if isinstance(ent, dict) and "name" in ent and "type" in ent:
                validated.append(
                    {
                        "name": str(ent["name"]).strip(),
                        "type": str(ent.get("type", "CONCEPT")).upper(),
                        "description": str(ent.get("description", "")),
                    }
                )
        logger.info("LLM extracted %d entities", len(validated))
        return validated

    def _regex_extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Naive fallback: extract capitalised noun phrases as CONCEPT entities.
        """
        # Match sequences of Title-Case words (2-4 consecutive)
        pattern = re.compile(r"\b(?:[A-Z][a-z]+\s){1,3}[A-Z][a-z]+\b")
        matches = set(pattern.findall(text))
        entities = [
            {"name": m.strip(), "type": "CONCEPT", "description": ""}
            for m in matches
        ]
        logger.info("Regex fallback extracted %d entities", len(entities))
        return entities

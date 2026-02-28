"""
General-purpose utility helpers for AgentGraph Intel.
"""
from __future__ import annotations

import hashlib
import re
import time
from functools import wraps
from typing import Any, Callable, List, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# String utilities
# ---------------------------------------------------------------------------


def truncate(text: str, max_length: int = 500, suffix: str = "…") -> str:
    """Truncate *text* to *max_length* characters, appending *suffix*."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def clean_whitespace(text: str) -> str:
    """Collapse consecutive whitespace and strip leading/trailing space."""
    return re.sub(r"\s+", " ", text).strip()


def slugify(text: str) -> str:
    """Convert *text* to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


# ---------------------------------------------------------------------------
# Hashing utilities
# ---------------------------------------------------------------------------


def sha256_hex(data: str) -> str:
    """Return the SHA-256 hex digest of *data*."""
    return hashlib.sha256(data.encode()).hexdigest()


def short_hash(data: str, length: int = 8) -> str:
    """Return a short hash of *data*."""
    return sha256_hex(data)[:length]


# ---------------------------------------------------------------------------
# List utilities
# ---------------------------------------------------------------------------


def deduplicate(items: List[Any], key: str = "id") -> List[Any]:
    """
    Remove duplicate dicts from *items* based on *key*.
    Preserves insertion order and keeps the first occurrence.
    """
    seen: set = set()
    result = []
    for item in items:
        k = item.get(key) if isinstance(item, dict) else item
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result


def flatten(nested: List[List[Any]]) -> List[Any]:
    """Flatten a one-level nested list."""
    return [item for sublist in nested for item in sublist]


# ---------------------------------------------------------------------------
# Timing decorator
# ---------------------------------------------------------------------------


def timed(logger=None):
    """
    Decorator that logs the execution time of a function.

    Usage::

        @timed(logger=my_logger)
        def slow_function():
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            msg = f"{func.__qualname__} completed in {elapsed:.1f} ms"
            if logger:
                logger.debug(msg)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


# ---------------------------------------------------------------------------
# Text splitting helpers
# ---------------------------------------------------------------------------


def split_into_sentences(text: str) -> List[str]:
    """Naively split text into sentences on common terminators."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def count_tokens_approx(text: str) -> int:
    """Approximate token count (1 token ≈ 4 characters for English text)."""
    return max(1, len(text) // 4)

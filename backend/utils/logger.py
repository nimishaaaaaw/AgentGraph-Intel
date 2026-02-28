"""
Centralised logging configuration for AgentGraph Intel.

Usage::

    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Hello")
"""
import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _configure_root() -> None:
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    # Avoid duplicate handlers if configure is called more than once
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # Quieten noisy third-party loggers
    for noisy in (
        "httpx",
        "httpcore",
        "urllib3",
        "neo4j",
        "chromadb",
        "sentence_transformers",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, ensuring root logging is configured."""
    _configure_root()
    return logging.getLogger(name)

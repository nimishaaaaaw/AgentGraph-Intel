"""
Health-check routes.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


class DetailedHealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic liveness probe."""
    from config import settings

    return HealthResponse(status="ok", version=settings.app_version)


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health():
    """Detailed health check — probes each downstream service."""
    from config import settings

    services: Dict[str, Any] = {}

    # ChromaDB
    try:
        from rag.vector_store import VectorStore

        store = VectorStore()
        chunk_count = store.count()
        services["chromadb"] = {"status": "ok", "chunks": chunk_count}
    except Exception as exc:
        services["chromadb"] = {"status": "error", "detail": str(exc)}

    # Neo4j
    try:
        from knowledge_graph.neo4j_client import Neo4jClient

        client = Neo4jClient()
        ok = client.health_check()
        services["neo4j"] = {"status": "ok" if ok else "unreachable"}
    except Exception as exc:
        services["neo4j"] = {"status": "error", "detail": str(exc)}

    # LLM
    try:
        from llm.llm_factory import LLMFactory

        llm = LLMFactory.get_llm()
        services["llm"] = {
            "status": "ok" if llm.is_available() else "no_api_key",
            "provider": settings.llm_provider,
        }
    except Exception as exc:
        services["llm"] = {"status": "error", "detail": str(exc)}

    overall = (
        "ok"
        if all(s.get("status") == "ok" for s in services.values())
        else "degraded"
    )

    return DetailedHealthResponse(
        status=overall,
        version=settings.app_version,
        services=services,
    )

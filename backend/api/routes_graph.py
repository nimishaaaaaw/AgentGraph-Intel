"""
Knowledge graph routes — query entities, relationships, and graph stats.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.graph_service import GraphService
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["graph"])

_graph_service = GraphService()


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class EntityModel(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class RelationshipModel(BaseModel):
    source: str
    relationship: str
    target: str
    description: Optional[str] = None


class GraphStatsModel(BaseModel):
    available: bool
    total_entities: Optional[int] = None
    total_relationships: Optional[int] = None
    entity_types: Optional[List[dict]] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/graph/entities", response_model=List[EntityModel])
async def get_entities(
    entity_type: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
):
    """Return entities stored in the knowledge graph, optionally filtered by type."""
    try:
        entities = _graph_service.get_entities(entity_type=entity_type, limit=limit)
        return [EntityModel(**e) for e in entities]
    except Exception as exc:
        logger.exception("get_entities error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/graph/relationships", response_model=List[RelationshipModel])
async def get_relationships(limit: int = Query(default=100, ge=1, le=1000)):
    """Return relationship triples from the knowledge graph."""
    try:
        rels = _graph_service.get_relationships(limit=limit)
        return [RelationshipModel(**r) for r in rels]
    except Exception as exc:
        logger.exception("get_relationships error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/graph/search")
async def search_graph(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Full-text search over entity names in the knowledge graph."""
    try:
        results = _graph_service.search_entities(search_term=q, limit=limit)
        return {"query": q, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/graph/neighbours/{entity_name}")
async def get_neighbours(
    entity_name: str,
    max_hops: int = Query(default=2, ge=1, le=3),
):
    """Return the neighbourhood graph for a given entity."""
    try:
        graph = _graph_service.get_entity_neighbours(entity_name, max_hops=max_hops)
        return {"entity": entity_name, "graph": graph}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/graph/stats", response_model=GraphStatsModel)
async def get_graph_stats():
    """Return basic statistics about the knowledge graph."""
    try:
        stats = _graph_service.get_stats()
        return GraphStatsModel(**stats)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

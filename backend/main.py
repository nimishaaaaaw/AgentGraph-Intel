"""
Main FastAPI application entry point.
Configures middleware, routers, and lifespan events.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.routes_chat import router as chat_router
from api.routes_documents import router as documents_router
from api.routes_graph import router as graph_router
from api.routes_health import router as health_router
from api.middleware import RequestLoggingMiddleware
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Shutting down AgentGraph Intel")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic AI Research Assistant powered by LangGraph, Neo4j, and Advanced RAG",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include all routers
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(graph_router, prefix="/api")
app.include_router(health_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint returning application information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Agentic AI Research Assistant",
        "docs": "/docs",
    }

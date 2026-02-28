# AgentGraph Intel

**Agentic AI Research Assistant powered by LangGraph, Neo4j, and Advanced RAG**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)

## Overview

AgentGraph Intel is a production-ready agentic AI research assistant that combines:

- **LangGraph** orchestration for multi-agent workflows
- **Neo4j** knowledge graph for entity relationships and structured retrieval
- **ChromaDB** vector store for semantic similarity search
- **Hybrid RAG** (dense + sparse retrieval with reranking)
- **Google Gemini** LLM for generation and reasoning
- **FastAPI** backend with streaming support

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI Backend                     │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┐  │
│  │  /chat   │  │/documents │  │    /graph        │  │
│  └────┬─────┘  └─────┬─────┘  └────────┬─────────┘  │
│       │              │                  │             │
│  ┌────▼──────────────▼──────────────────▼─────────┐  │
│  │              LangGraph Orchestrator              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  │
│  │  │Researcher│  │KG Builder│  │   Analyst    │  │  │
│  │  │  Agent   │  │  Agent   │  │    Agent     │  │  │
│  │  └────┬─────┘  └─────┬────┘  └──────┬───────┘  │  │
│  └───────┼──────────────┼──────────────┼───────────┘  │
│          │              │              │               │
│  ┌───────▼──────┐ ┌─────▼──────┐      │               │
│  │  Hybrid RAG  │ │  Neo4j KG  │      │               │
│  │  ChromaDB +  │ │  Entities  │      │               │
│  │  BM25 + Rerank│ │ Relations │      │               │
│  └──────────────┘ └────────────┘      │               │
│                                        │               │
│  ┌─────────────────────────────────────▼───────────┐  │
│  │              Google Gemini 2.0 Flash              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Features

- 🤖 **Multi-Agent Orchestration** — Specialized agents for research, KG building, and analysis
- 🔍 **Hybrid Retrieval** — Dense (ChromaDB) + Sparse (BM25) with cross-encoder reranking
- 🕸️ **Knowledge Graph RAG** — Entity extraction and graph traversal for structured reasoning
- 📄 **Document Processing** — PDF, TXT, and Markdown ingestion with intelligent chunking
- 💬 **Streaming Chat** — Server-Sent Events for real-time response streaming
- 🏥 **Health Monitoring** — Detailed health checks for all service dependencies

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Neo4j 5.x (local or AuraDB)
- Google Gemini API key

### Local Development

```bash
# Clone repository
git clone https://github.com/your-org/AgentGraph-Intel.git
cd AgentGraph-Intel

# Backend setup
cp .env.example .env
# Edit .env with your credentials

cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend setup (separate terminal)
cd frontend
npm install
npm run dev
```

### Docker

```bash
cp .env.example .env
# Edit .env with your credentials
docker-compose up -d --build
```

Services will be available at:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Neo4j Browser**: http://localhost:7474

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a chat message |
| POST | `/api/chat/stream` | Streaming chat response |
| GET | `/api/chat/history/{session_id}` | Get chat history |
| POST | `/api/documents/upload` | Upload documents |
| GET | `/api/documents` | List documents |
| DELETE | `/api/documents/{doc_id}` | Delete a document |
| GET | `/api/graph/entities` | List graph entities |
| GET | `/api/graph/relationships` | List relationships |
| GET | `/api/graph/search` | Search the knowledge graph |
| GET | `/api/health` | Health check |
| GET | `/api/health/detailed` | Detailed service health |

## Project Structure

```
AgentGraph-Intel/
├── backend/
│   ├── agents/           # LangGraph agent definitions
│   │   ├── orchestrator.py   # Main workflow graph
│   │   ├── researcher_agent.py
│   │   ├── kg_builder_agent.py
│   │   ├── analyst_agent.py
│   │   ├── router.py
│   │   └── state.py
│   ├── rag/              # Retrieval-Augmented Generation
│   │   ├── document_processor.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   └── query_engine.py
│   ├── knowledge_graph/  # Neo4j integration
│   │   ├── neo4j_client.py
│   │   ├── entity_extractor.py
│   │   ├── relationship_builder.py
│   │   ├── graph_query.py
│   │   └── graph_rag.py
│   ├── llm/              # LLM abstraction layer
│   │   ├── llm_factory.py
│   │   ├── prompts.py
│   │   └── output_parsers.py
│   ├── api/              # FastAPI routes & middleware
│   │   ├── routes_chat.py
│   │   ├── routes_documents.py
│   │   ├── routes_graph.py
│   │   ├── routes_health.py
│   │   └── middleware.py
│   ├── services/         # Business logic layer
│   │   ├── chat_service.py
│   │   ├── document_service.py
│   │   └── graph_service.py
│   ├── utils/
│   │   ├── logger.py
│   │   └── helpers.py
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   └── setup_guide.md
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── Makefile
└── .env.example
```

## Configuration

All configuration is via environment variables. See [`.env.example`](.env.example) for all options.

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | required |
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_data` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

## Testing

```bash
cd backend
pytest tests/ -v
pytest tests/unit/ -v        # Unit tests only
pytest tests/integration/ -v  # Integration tests
```

## Documentation

- [Architecture Guide](docs/architecture.md)
- [API Reference](docs/api_reference.md)
- [Setup Guide](docs/setup_guide.md)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

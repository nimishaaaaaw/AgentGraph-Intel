# AgentGraph Intel — API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## Authentication

Currently no authentication is required. For production deployments, add an API key header middleware.

---

## Endpoints

### Root

#### `GET /`

Returns application metadata.

**Response**
```json
{
  "name": "AgentGraph Intel",
  "version": "1.0.0",
  "description": "Agentic AI Research Assistant",
  "docs": "/docs"
}
```

---

### Health

#### `GET /api/health`

Liveness probe.

**Response** `200 OK`
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

#### `GET /api/health/detailed`

Detailed health check including all downstream service probes.

**Response** `200 OK`
```json
{
  "status": "ok",
  "version": "1.0.0",
  "services": {
    "chromadb": { "status": "ok", "chunks": 142 },
    "neo4j":    { "status": "ok" },
    "llm":      { "status": "ok", "provider": "gemini" }
  }
}
```

Possible `status` values: `"ok"`, `"degraded"`, `"error"`, `"unreachable"`, `"no_api_key"`

---

### Chat

#### `POST /api/chat`

Send a message and receive a complete response.

**Request Body**
```json
{
  "message": "What is LangGraph?",
  "session_id": "user-abc-123",
  "history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help?" }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ | 1–4000 chars |
| `session_id` | string | ❌ | Defaults to `"default"` |
| `history` | array | ❌ | Prior conversation turns |

**Response** `200 OK`
```json
{
  "answer": "LangGraph is a library for building stateful multi-agent applications...",
  "session_id": "user-abc-123",
  "sources": [
    {
      "content": "LangGraph enables...",
      "source": "langgraph-docs.pdf",
      "filename": "langgraph-docs.pdf",
      "score": 0.94
    }
  ],
  "steps_taken": ["router:researcher", "researcher", "synthesiser"]
}
```

---

#### `POST /api/chat/stream`

Streaming chat using Server-Sent Events (SSE).

**Request Body** — same as `/api/chat`

**Response** `200 OK` with `Content-Type: text/event-stream`

Each event is a JSON object on a `data:` line:

```
data: {"chunk": "LangGraph is a lib", "done": false}

data: {"chunk": "rary for building...", "done": false}

data: {"chunk": "", "done": true, "sources": [...], "steps_taken": [...]}
```

---

#### `GET /api/chat/history/{session_id}`

Retrieve conversation history for a session.

**Path Parameters**

| Param | Description |
|-------|-------------|
| `session_id` | Session identifier |

**Response** `200 OK`
```json
{
  "session_id": "user-abc-123",
  "history": [
    { "role": "user", "content": "What is LangGraph?" },
    { "role": "assistant", "content": "LangGraph is..." }
  ]
}
```

---

#### `DELETE /api/chat/history/{session_id}`

Clear conversation history for a session.

**Response** `200 OK`
```json
{ "message": "History cleared for session 'user-abc-123'" }
```

---

### Documents

#### `POST /api/documents/upload`

Upload a document for ingestion into the RAG pipeline.

**Content-Type**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | ✅ | PDF, TXT, or Markdown |
| `description` | string | ❌ | Optional document description |

**Response** `200 OK`
```json
{
  "message": "Document uploaded and indexed successfully",
  "doc_id": "a1b2c3d4",
  "filename": "research-paper.pdf",
  "chunks_created": 47
}
```

**Error Responses**

| Status | Reason |
|--------|--------|
| `400` | Unsupported file type |
| `500` | Processing / embedding failure |

---

#### `GET /api/documents`

List all ingested documents.

**Response** `200 OK`
```json
[
  {
    "doc_id": "a1b2c3d4",
    "filename": "research-paper.pdf",
    "source": "research-paper.pdf"
  }
]
```

---

#### `DELETE /api/documents/{doc_id}`

Delete a document and all its chunks from the vector store.

**Response** `200 OK`
```json
{ "message": "Document 'a1b2c3d4' deleted successfully" }
```

---

#### `GET /api/documents/{doc_id}/chunks`

Retrieve stored chunks for a document (debugging).

**Query Parameters**

| Param | Default | Description |
|-------|---------|-------------|
| `limit` | `20` | Max chunks to return |

**Response** `200 OK`
```json
{
  "doc_id": "a1b2c3d4",
  "chunks": [
    {
      "chunk_id": "a1b2c3d4-0",
      "content": "First chunk text...",
      "metadata": { "filename": "research-paper.pdf", "chunk_index": 0 }
    }
  ]
}
```

---

### Knowledge Graph

#### `GET /api/graph/entities`

Return entities from the knowledge graph.

**Query Parameters**

| Param | Default | Description |
|-------|---------|-------------|
| `entity_type` | `null` | Filter by type (e.g. `TECHNOLOGY`) |
| `limit` | `100` | Max entities to return |

**Response** `200 OK`
```json
[
  { "name": "LangGraph", "type": "TECHNOLOGY", "description": "..." },
  { "name": "Neo4j", "type": "TECHNOLOGY", "description": "..." }
]
```

---

#### `GET /api/graph/relationships`

Return relationship triples.

**Query Parameters**

| Param | Default | Description |
|-------|---------|-------------|
| `limit` | `100` | Max relationships |

**Response** `200 OK`
```json
[
  {
    "source": "LangGraph",
    "relationship": "CREATED_BY",
    "target": "LangChain",
    "description": "LangGraph was created by LangChain Inc."
  }
]
```

---

#### `GET /api/graph/search`

Full-text search over entity names.

**Query Parameters**

| Param | Required | Description |
|-------|----------|-------------|
| `q` | ✅ | Search term |
| `limit` | ❌ | Max results (default 20) |

**Response** `200 OK`
```json
{
  "query": "lang",
  "results": [
    { "name": "LangGraph", "type": "TECHNOLOGY", "description": "..." },
    { "name": "LangChain", "type": "ORGANIZATION", "description": "..." }
  ]
}
```

---

#### `GET /api/graph/neighbours/{entity_name}`

Return the neighbourhood graph for an entity.

**Path Parameters**

| Param | Description |
|-------|-------------|
| `entity_name` | Exact entity name |

**Query Parameters**

| Param | Default | Description |
|-------|---------|-------------|
| `max_hops` | `2` | Graph traversal depth (1–3) |

**Response** `200 OK`
```json
{
  "entity": "LangGraph",
  "graph": {
    "nodes": [
      { "name": "LangGraph", "type": "TECHNOLOGY" },
      { "name": "LangChain", "type": "ORGANIZATION" }
    ],
    "edges": [
      { "source": "LangGraph", "target": "LangChain", "relationship": "CREATED_BY" }
    ]
  }
}
```

---

#### `GET /api/graph/stats`

Return knowledge graph statistics.

**Response** `200 OK`
```json
{
  "available": true,
  "total_entities": 342,
  "total_relationships": 891,
  "entity_types": [
    { "type": "TECHNOLOGY", "count": 120 },
    { "type": "ORGANIZATION", "count": 85 }
  ]
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status | Description |
|--------|-------------|
| `400` | Bad request (validation, unsupported file type) |
| `422` | Unprocessable entity (Pydantic validation failure) |
| `500` | Internal server error |

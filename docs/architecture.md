# AgentGraph Intel — Architecture Guide

## Overview

AgentGraph Intel is built around three core pillars:

1. **Multi-Agent Orchestration** via LangGraph
2. **Hybrid Retrieval-Augmented Generation (RAG)**
3. **Knowledge Graph Integration** via Neo4j

---

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│                                                             │
│  ┌────────────┐  ┌───────────────┐  ┌───────────────────┐  │
│  │ /api/chat  │  │ /api/documents│  │    /api/graph     │  │
│  └─────┬──────┘  └───────┬───────┘  └─────────┬─────────┘  │
│        │                 │                     │             │
│  ┌─────▼─────────────────▼─────────────────────▼──────────┐ │
│  │                  Service Layer                           │ │
│  │  ChatService  │  DocumentService  │  GraphService        │ │
│  └─────┬─────────────────┬───────────────────┬─────────────┘ │
│        │                 │                   │               │
│  ┌─────▼─────────────────┼───────────────────┼────────────┐  │
│  │         LangGraph Orchestrator             │            │  │
│  │                                            │            │  │
│  │  ┌──────────┐  ┌─────────────┐  ┌──────────────────┐   │  │
│  │  │  Router  │→ │ Researcher  │  │   KG Builder     │   │  │
│  │  │          │→ │   Agent     │  │     Agent        │   │  │
│  │  │          │→ │  Analyst    │  │                  │   │  │
│  │  └──────────┘  │   Agent     │  │                  │   │  │
│  │                └──────┬──────┘  └─────────┬────────┘   │  │
│  │                       └────────┬───────────┘            │  │
│  │                          ┌─────▼──────┐                 │  │
│  │                          │Synthesiser │                 │  │
│  │                          └────────────┘                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────┐    ┌──────────────────────────────┐  │
│  │    Hybrid RAG       │    │    Knowledge Graph           │  │
│  │                     │    │                              │  │
│  │  ChromaDB (dense)   │    │  Neo4j (entities/relations)  │  │
│  │  BM25 (sparse)      │    │  Entity Extractor            │  │
│  │  Cross-Encoder Rerank│   │  Relationship Builder        │  │
│  └────────────────────┘    └──────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Google Gemini 2.0 Flash LLM                │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## Component Deep-Dives

### 1. LangGraph Orchestrator (`agents/orchestrator.py`)

The orchestrator compiles a `StateGraph` using LangGraph:

```
router → [researcher | kg_builder | analyst] → synthesiser → END
```

**State** (`agents/state.py`) is a `TypedDict` passed between all nodes:
- Input: `query`, `session_id`
- Routing: `route`
- RAG outputs: `retrieved_docs`, `rag_answer`
- KG outputs: `extracted_entities`, `extracted_relationships`, `kg_context`
- Analysis: `analysis`, `citations`
- Final: `final_answer`, `sources`

**Routing logic** (`agents/router.py`):
- Contains KG keywords → `kg_builder`
- Contains analytical keywords → `analyst`
- Default → `researcher`

### 2. Hybrid RAG Pipeline

```
Query → Embedder → ChromaDB (dense, top-20)
                     ↓
Query → BM25 over candidates (sparse, top-20)
                     ↓
         RRF Fusion (final top-10)
                     ↓
         Cross-Encoder Reranker (top-5)
                     ↓
         LLM Generation
```

**Reciprocal Rank Fusion (RRF)**:
```
score(d) = Σ weight_i / (k + rank_i(d))
```
where `k=60` and dense_weight=0.6, sparse_weight=0.4.

### 3. Knowledge Graph (Neo4j)

**Entity types**: PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, CONCEPT, EVENT, PRODUCT, DATE

**Graph schema**:
```
(:Entity {name, type, description}) -[:RELATIONSHIP_TYPE {description}]-> (:Entity)
(:Document {doc_id, filename})
```

**Graph RAG**: For each extracted entity, fetch 1-hop neighbours from Neo4j and format them as additional LLM context.

### 4. LLM Abstraction (`llm/llm_factory.py`)

The `LLMFactory` returns a `BaseLLM` implementation:
- **GeminiLLM** — Google Gemini 2.0 Flash via `google-generativeai` SDK
- **GroqLLM** — Groq inference API via `httpx`
- **MockLLM** — Used in tests and when no API key is configured

### 5. Document Processing (`rag/document_processor.py`)

Supported formats: PDF (via PyPDF2), TXT, Markdown

Chunking strategy:
1. Split on paragraph boundaries
2. Within paragraphs, split on sentence boundaries
3. Accumulate chunks of ≤800 chars with 150-char overlap

---

## Data Flow: Chat Request

```
POST /api/chat
  │
  └─ ChatService.chat(message, session_id)
       │
       └─ run_agent(query, session_id)  [LangGraph]
            │
            ├─ router node → determines route
            │
            ├─ researcher node (if route == "researcher")
            │   ├─ QueryEngine.query(question)
            │   │   ├─ HybridRetriever.retrieve()
            │   │   │   ├─ EmbeddingService.embed_query()
            │   │   │   ├─ VectorStore.similarity_search()  [ChromaDB]
            │   │   │   └─ BM25 scoring + RRF fusion
            │   │   ├─ Reranker.rerank()  [CrossEncoder]
            │   │   └─ LLMFactory.get_llm().generate()  [Gemini]
            │   └─ returns retrieved_docs + rag_answer
            │
            ├─ synthesiser node
            │   └─ LLMFactory.get_llm().generate()  [optional]
            │
            └─ returns AgentState with final_answer
```

## Data Flow: Document Upload

```
POST /api/documents/upload
  │
  └─ DocumentService.ingest_bytes(content, filename)
       │
       ├─ DocumentProcessor.process_file()
       │   ├─ Extract text (PyPDF2 / plain text)
       │   └─ Split into chunks
       │
       ├─ EmbeddingService.embed_texts()
       │   └─ SentenceTransformer("all-MiniLM-L6-v2")
       │
       └─ VectorStore.add_documents()
           └─ ChromaDB upsert
```

---

## Scalability Considerations

| Component | Current | Production Recommendation |
|-----------|---------|--------------------------|
| Session store | In-memory dict | Redis |
| Vector store | Local ChromaDB | ChromaDB Cloud or Pinecone |
| Neo4j | Local / AuraDB Free | AuraDB Professional |
| LLM | Gemini Flash | Add request batching + rate limiting |
| API | Single process | Gunicorn with multiple workers |

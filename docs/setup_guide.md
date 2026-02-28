# AgentGraph Intel — Setup Guide

## Prerequisites

| Dependency | Minimum Version | Notes |
|------------|----------------|-------|
| Python | 3.11 | Required for `tomllib` in stdlib |
| Node.js | 20.x | For frontend |
| Neo4j | 5.x | Local or AuraDB |
| Google Gemini API | — | Free tier available |

---

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/AgentGraph-Intel.git
cd AgentGraph-Intel
```

---

## 2. Environment Configuration

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required: LLM
GEMINI_API_KEY=your_gemini_api_key_here

# Required: Neo4j (use AuraDB free tier or local)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Optional: override defaults
CHROMA_PERSIST_DIR=./chroma_data
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **Create API key**
3. Copy the key into `GEMINI_API_KEY`

### Neo4j Setup Options

**Option A — Local Docker**
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5.16
```
Then set `NEO4J_URI=bolt://localhost:7687` and `NEO4J_PASSWORD=password123`.

**Option B — Neo4j AuraDB (Free)**
1. Sign up at [console.neo4j.io](https://console.neo4j.io)
2. Create a free instance
3. Copy the connection URI (starts with `neo4j+s://`)

---

## 3. Backend Setup

```bash
cd backend

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Verify the backend is running

```bash
curl http://localhost:8000/api/health
# {"status":"ok","version":"1.0.0"}
```

---

## 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173.

---

## 5. Docker Compose (All Services)

To run the full stack (backend + frontend + Neo4j):

```bash
# Ensure .env is configured
docker-compose up -d --build

# Check logs
docker-compose logs -f backend
```

Services:
| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| Frontend | http://localhost:3000 |
| Neo4j Browser | http://localhost:7474 |

---

## 6. First Use — Ingest a Document

```bash
# Upload a PDF
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/your/document.pdf"

# Or a text file
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/notes.txt"
```

---

## 7. Send Your First Chat Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main topics in the documents?"}'
```

---

## 8. Running Tests

```bash
cd backend

# All tests
pytest tests/ -v

# Unit tests only (fast, no external dependencies)
pytest tests/unit/ -v

# Integration tests (external deps mocked)
pytest tests/integration/ -v

# With coverage report
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

---

## 9. Troubleshooting

### ChromaDB "Collection not found" error

ChromaDB creates the collection on first run. If you see errors:

```bash
# Delete the persisted data and let it recreate
rm -rf backend/chroma_data
```

### Neo4j connection refused

Check that Neo4j is running and the URI/credentials in `.env` are correct:

```bash
# Test with cypher-shell (if installed)
cypher-shell -a bolt://localhost:7687 -u neo4j -p your_password "RETURN 1"
```

### Gemini "API key not valid" error

Double-check the `GEMINI_API_KEY` in your `.env`. The app will fall back to `MockLLM` if no valid key is found — look for `"MockLLM is active"` in the logs.

### sentence-transformers download slow

The first run downloads the `all-MiniLM-L6-v2` model (~90 MB). Subsequent runs use the local cache at `~/.cache/torch/sentence_transformers/`.

### Port 8000 already in use

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

---

## 10. Production Deployment Checklist

- [ ] Set `DEBUG=false` in `.env`
- [ ] Use a proper secret for Neo4j credentials
- [ ] Configure `CORS_ORIGINS` to your frontend domain only
- [ ] Run behind a reverse proxy (nginx) with TLS
- [ ] Replace in-memory session store with Redis
- [ ] Set up log aggregation (e.g. Datadog, ELK)
- [ ] Enable Neo4j authentication and use AuraDB
- [ ] Configure Gunicorn workers: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker`

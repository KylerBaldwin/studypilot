# Group 6 Agentic AI Capstone - StudyPilot

An AI study assistant with Canvas LMS integration. Ask about your courses, upcoming assignments, and more.

## Stack

- **Frontend** — Streamlit (`ui/`)
- **Backend** — FastAPI + LangGraph ReAct agent (`backend/`)
- **Canvas MCP** — FastMCP server exposing Canvas LMS tools over SSE (`mcp/canvas/`)
- **RAG** — ChromaDB with pre-seeded course syllabi (`backend/rag/`)
- **LLM** — OpenAI (configurable model via `OPENAI_MODEL`)
- **Observability** — LangSmith tracing + per-response helpfulness eval

## Local dev

Prerequisites: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

Copy each service's `.env.example` to `.env` and fill in the values, then:

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8501 |
| Backend API docs | http://localhost:8000/docs |
| Canvas MCP | http://localhost:8001/sse |

### Testing the Canvas MCP in isolation

```bash
cd mcp/canvas
uv run fastmcp dev inspector server.py
```

### Seeding the RAG document store

Drop course syllabi or any text files into `backend/rag/seed/`, then run:

```powershell
cd backend; $env:CHROMA_PERSIST_DIR="./data/chroma"; uv run python rag/seed.py
```

The seeded ChromaDB is committed to the repo at `backend/data/chroma/` and baked into the Docker image at build time — no separate seeding step needed on Railway.

## Environment variables

See each service's `.env.example` for the full list. Key variables:

| Variable | Service | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | backend | OpenAI API key |
| `CANVAS_TOKEN` | canvas-mcp | Canvas LMS access token |
| `CANVAS_BASE_URL` | canvas-mcp, backend | Your institution's Canvas domain |
| `CANVAS_MCP_URL` | backend | Set automatically in docker-compose |
| `LANGCHAIN_API_KEY` | backend | LangSmith API key |
| `LANGCHAIN_TRACING_V2` | backend | Enable LangSmith tracing |
| `FRONTEND_URL` | backend | CORS origin |
| `API_URL` | frontend | Backend base URL |

## Project structure

```
study-pilot/
├── docker-compose.yml
├── ui/                        # Streamlit frontend
│   ├── app.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .streamlit/
│       └── config.toml
├── backend/                   # FastAPI + LangGraph agent
│   ├── main.py                # /chat streaming endpoint
│   ├── config.py
│   ├── agents/
│   │   └── canvas.py          # ReAct agent + LangSmith eval
│   ├── rag/
│   │   ├── ingest.py          # chunk + embed documents
│   │   ├── retrieve.py        # semantic search
│   │   ├── seed.py            # one-time seeding script
│   │   └── seed/              # drop syllabi here before seeding
│   ├── data/chroma/           # pre-seeded ChromaDB (committed)
│   ├── Dockerfile
│   └── pyproject.toml
└── mcp/
    └── canvas/                # FastMCP Canvas LMS server
        ├── server.py
        ├── utils.py
        ├── Dockerfile
        └── pyproject.toml
```

## Deployment (Railway)

Deploy `frontend`, `backend`, and `canvas-mcp` as three separate Railway services in the same project. They communicate over Railway's private network.

1. Connect your GitHub repo to Railway
2. Set environment variables on each service (see `.env.example` files)
3. Set `CANVAS_MCP_URL=http://canvas-mcp.railway.internal:8001/sse` on the backend service
4. Set `API_URL=https://your-backend.railway.app` on the frontend service

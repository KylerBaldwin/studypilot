# StudyPilot

A student AI assistant with RAG over course materials, Canvas LMS integration, and flashcard generation.

## Stack

- **Frontend** — Streamlit (`ui/`)
- **Backend** — FastAPI + LangGraph ReAct agent (`backend/`)
- **MCP server** — Canvas LMS via stdio subprocess (`mcp/canvas/`)
- **Vector store** — ChromaDB (embedded, persisted to volume)
- **Auth** — Google OAuth + Fernet-encrypted token storage

## Local dev

```bash
cp ui/.env.example ui/.env
cp backend/.env.example backend/.env
# fill in both .env files

docker compose up
```

Frontend: http://localhost:8501  
Backend: http://localhost:8000/docs

## Project structure

```
study-pilot/
├── docker-compose.yml
├── ui/                  # Streamlit frontend
├── backend/             # FastAPI backend + LangGraph agent
└── mcp/
    └── canvas/          # Canvas MCP server (stdio)
```

## Setup

See `.env.example` files in `ui/` and `backend/` for required environment variables and how to generate them.

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from rag.demo_loader import ensure_demo_collection
from routes import auth, chat, rag, flashcards

app = FastAPI(title="StudyPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_upload_bytes:
            return JSONResponse(status_code=413, content={"detail": "File too large"})
    return await call_next(request)


@app.on_event("startup")
async def startup():
    ensure_demo_collection()


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(flashcards.router)


@app.get("/health")
def health():
    return {"status": "ok"}

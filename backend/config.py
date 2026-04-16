from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Canvas
    canvas_base_url: str = "https://canvas.instructure.com"
    canvas_mcp_url: str = "http://localhost:8001/sse"

    # URLs
    frontend_url: str = "http://localhost:8501"

    # Storage
    chroma_persist_dir: str = "/app/data/chroma"
    db_path: str = "/app/data/studypilot.db"

    # Upload limit (bytes)
    max_upload_bytes: int = 50 * 1024 * 1024  # 50 MB

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "study-pilot"


settings = Settings()

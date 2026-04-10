from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Google OAuth
    google_client_id: str
    google_client_secret: str

    # Token encryption (Fernet key)
    token_encryption_key: str

    # Canvas
    canvas_base_url: str = "https://canvas.instructure.com"

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

    @property
    def auth_enabled(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret)

    @property
    def token_store_enabled(self) -> bool:
        return bool(self.token_encryption_key)


settings = Settings()

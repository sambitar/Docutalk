from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://docutalk:docutalk@localhost:5433/docutalk"
    jwt_secret: str = "change-me-in-production-use-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    docutalk_secrets_key: str = "0123456789abcdef0123456789abcdef"  # 32 bytes hex for AES-256
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 5
    max_documents_per_workspace: int = 20
    max_upload_bytes: int = 10 * 1024 * 1024
    max_pdf_pages: int = 200
    chat_rate_limit_per_hour: int = 60
    cors_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()

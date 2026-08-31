from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.db import engine
from app.middleware_rate_limit import SimpleRateLimitMiddleware
from app.routers import auth, chat, documents, workspaces
from app.routers.auth import me_router
from app.schemas import HealthResponse

settings = get_settings()

app = FastAPI(title="Docutalk API", version="0.1.0")

app.add_middleware(SimpleRateLimitMiddleware, limit=120, window_seconds=60.0)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(me_router)
app.include_router(workspaces.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return HealthResponse(status="ok", database="ok")
    except Exception:
        return HealthResponse(status="degraded", database="error")

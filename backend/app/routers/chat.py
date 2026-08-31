from collections import defaultdict
from time import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.deps import get_owned_workspace
from app.models import Workspace
from app.schemas import ChatRequest, ChatResponse
from app.security.crypto import decrypt_secret
from app.services.generate import generate_answer
from app.services.openai_client import embed_texts
from app.services.retrieve import similarity_search

router = APIRouter(prefix="/workspaces", tags=["chat"])

# Simple in-memory sliding window: workspace_id -> list of timestamps
_chat_hits: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(workspace_id: str, limit: int) -> None:
    now = time()
    window = 3600.0
    hits = [t for t in _chat_hits[workspace_id] if now - t < window]
    if len(hits) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Chat rate limit exceeded ({limit}/hour)",
        )
    hits.append(now)
    _chat_hits[workspace_id] = hits


@router.post("/{workspace_id}/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    workspace: Workspace = Depends(get_owned_workspace),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    settings = get_settings()
    if workspace.openai_api_key_encrypted is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured for this workspace",
        )

    _check_rate_limit(str(workspace.id), settings.chat_rate_limit_per_hour)

    api_key = decrypt_secret(workspace.openai_api_key_encrypted)
    vectors = await embed_texts(api_key, [body.question], settings.embedding_model)
    query_vec = vectors[0]
    chunks = await similarity_search(db, workspace.id, query_vec, settings.top_k)
    answer, sources = await generate_answer(
        api_key, settings.chat_model, body.question, chunks
    )
    return ChatResponse(answer=answer, sources=sources)

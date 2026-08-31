from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from openai import AuthenticationError, OpenAIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_owned_workspace
from app.models import Workspace
from app.schemas import OpenAIKeyRequest, OpenAIKeyResponse
from app.security.crypto import encrypt_secret, key_last4
from app.services.openai_client import validate_openai_key

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.put("/{workspace_id}/openai-key", response_model=OpenAIKeyResponse)
async def set_openai_key(
    body: OpenAIKeyRequest,
    workspace: Workspace = Depends(get_owned_workspace),
    db: AsyncSession = Depends(get_db),
) -> OpenAIKeyResponse:
    api_key = body.api_key.strip()
    try:
        await validate_openai_key(api_key)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OpenAI API key"
        ) from exc
    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"OpenAI key validation failed: {exc}"
        ) from exc

    workspace.openai_api_key_encrypted = encrypt_secret(api_key)
    workspace.openai_key_last4 = key_last4(api_key)
    workspace.openai_key_validated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(workspace)
    assert workspace.openai_key_last4 is not None
    assert workspace.openai_key_validated_at is not None
    return OpenAIKeyResponse(
        openai_key_last4=workspace.openai_key_last4,
        openai_key_validated_at=workspace.openai_key_validated_at,
    )

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.deps import get_owned_workspace
from app.models import Document, Workspace
from app.schemas import DocumentOut
from app.services.ingest import ingest_document

router = APIRouter(prefix="/workspaces", tags=["documents"])


@router.post("/{workspace_id}/documents", response_model=DocumentOut)
async def upload_document(
    workspace: Workspace = Depends(get_owned_workspace),
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
) -> DocumentOut:
    settings = get_settings()
    doc = await ingest_document(db, workspace, file, settings)
    return DocumentOut.model_validate(doc)


@router.get("/{workspace_id}/documents", response_model=list[DocumentOut])
async def list_documents(
    workspace: Workspace = Depends(get_owned_workspace),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentOut]:
    result = await db.execute(
        select(Document)
        .where(Document.workspace_id == workspace.id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    return [DocumentOut.model_validate(d) for d in docs]


@router.delete("/{workspace_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    workspace: Workspace = Depends(get_owned_workspace),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.workspace_id == workspace.id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    await db.delete(doc)
    await db.commit()

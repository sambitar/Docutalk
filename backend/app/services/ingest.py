import io
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.models import Chunk, Document, Workspace
from app.security.crypto import decrypt_secret
from app.services.openai_client import embed_texts


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    cleaned = re.sub(r"\r\n?", "\n", text).strip()
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + chunk_size, length)
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        start = max(end - overlap, start + 1)
    return chunks


def extract_text_from_upload(filename: str, data: bytes, max_pages: int) -> tuple[str, list[dict]]:
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md", ".markdown"}:
        text = data.decode("utf-8", errors="replace")
        return text, [{"page": None, "text": text}]

    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        if len(reader.pages) > max_pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDF exceeds max pages ({max_pages})",
            )
        pages: list[dict] = []
        parts: list[str] = []
        for i, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            pages.append({"page": i, "text": page_text})
            if page_text.strip():
                parts.append(f"[Page {i}]\n{page_text}")
        return "\n\n".join(parts), pages

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type. Allowed: PDF, TXT, MD",
    )


async def ingest_document(
    db: AsyncSession,
    workspace: Workspace,
    upload: UploadFile,
    settings: Settings,
) -> Document:
    if workspace.openai_api_key_encrypted is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured for this workspace",
        )

    count_result = await db.execute(
        select(func.count()).select_from(Document).where(Document.workspace_id == workspace.id)
    )
    doc_count = int(count_result.scalar_one())
    if doc_count >= settings.max_documents_per_workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document limit reached ({settings.max_documents_per_workspace})",
        )

    data = await upload.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds max size ({settings.max_upload_bytes} bytes)",
        )

    filename = upload.filename or "upload.txt"
    text, _pages = extract_text_from_upload(filename, data, settings.max_pdf_pages)
    pieces = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    if not pieces:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extractable text in document",
        )

    api_key = decrypt_secret(workspace.openai_api_key_encrypted)
    vectors = await embed_texts(api_key, pieces, settings.embedding_model)

    title = Path(filename).stem or filename
    doc = Document(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        title=title,
        source_filename=filename,
        byte_size=len(data),
    )
    db.add(doc)
    await db.flush()

    for idx, (content, embedding) in enumerate(zip(pieces, vectors, strict=True)):
        page = None
        m = re.search(r"\[Page (\d+)\]", content)
        if m:
            page = int(m.group(1))
        db.add(
            Chunk(
                id=uuid.uuid4(),
                workspace_id=workspace.id,
                document_id=doc.id,
                content=content,
                chunk_index=idx,
                metadata_json={"page": page, "title": title},
                embedding=embedding,
            )
        )

    await db.commit()
    await db.refresh(doc)
    return doc

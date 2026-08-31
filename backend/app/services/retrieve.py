from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class RetrievedChunk:
    id: UUID
    document_id: UUID
    content: str
    page: int | None
    distance: float


async def similarity_search(
    db: AsyncSession,
    workspace_id: UUID,
    query_embedding: list[float],
    top_k: int,
) -> list[RetrievedChunk]:
    vector_literal = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
    sql = text(
        """
        SELECT id, document_id, content, metadata, embedding <=> CAST(:embedding AS vector) AS distance
        FROM chunks
        WHERE workspace_id = :workspace_id
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
        """
    )
    result = await db.execute(
        sql,
        {
            "embedding": vector_literal,
            "workspace_id": str(workspace_id),
            "top_k": top_k,
        },
    )
    rows = result.mappings().all()
    chunks: list[RetrievedChunk] = []
    for row in rows:
        meta = row["metadata"] or {}
        page = meta.get("page") if isinstance(meta, dict) else None
        chunks.append(
            RetrievedChunk(
                id=row["id"],
                document_id=row["document_id"],
                content=row["content"],
                page=page,
                distance=float(row["distance"]),
            )
        )
    return chunks

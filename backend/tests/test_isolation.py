"""Cross-tenant isolation: retrieve must never return another workspace's chunks."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.deps import create_access_token, hash_password
from app.main import app
from app.models import Chunk, Document, User, Workspace
from app.services.retrieve import similarity_search


@pytest.fixture
async def session_factory():
    settings = get_settings()
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


async def _seed_two_workspaces(session_factory):
    async with session_factory() as db:
        u1 = User(email=f"a-{uuid.uuid4()}@example.com", password_hash=hash_password("password123"))
        u2 = User(email=f"b-{uuid.uuid4()}@example.com", password_hash=hash_password("password123"))
        db.add_all([u1, u2])
        await db.flush()
        w1 = Workspace(name="A", owner_user_id=u1.id)
        w2 = Workspace(name="B", owner_user_id=u2.id)
        db.add_all([w1, w2])
        await db.flush()

        d1 = Document(
            workspace_id=w1.id,
            title="SecretA",
            source_filename="a.txt",
            byte_size=10,
        )
        d2 = Document(
            workspace_id=w2.id,
            title="SecretB",
            source_filename="b.txt",
            byte_size=10,
        )
        db.add_all([d1, d2])
        await db.flush()

        emb_a = [0.01] * 1536
        emb_b = [0.99] * 1536
        c1 = Chunk(
            workspace_id=w1.id,
            document_id=d1.id,
            content="workspace A confidential alpha",
            chunk_index=0,
            metadata_json={"page": 1},
            embedding=emb_a,
        )
        c2 = Chunk(
            workspace_id=w2.id,
            document_id=d2.id,
            content="workspace B confidential beta",
            chunk_index=0,
            metadata_json={"page": 1},
            embedding=emb_b,
        )
        db.add_all([c1, c2])
        await db.commit()
        return {
            "w1_id": w1.id,
            "w2_id": w2.id,
            "emb_a": emb_a,
            "emb_b": emb_b,
            "u1_id": u1.id,
            "u2_id": u2.id,
        }


@pytest.mark.asyncio
async def test_retrieve_scoped_to_workspace(session_factory):
    seeded = await _seed_two_workspaces(session_factory)
    async with session_factory() as db:
        hits_a = await similarity_search(db, seeded["w1_id"], seeded["emb_a"], top_k=5)
        hits_b = await similarity_search(db, seeded["w2_id"], seeded["emb_b"], top_k=5)

    assert hits_a
    assert all("workspace A" in h.content for h in hits_a)
    assert all("workspace B" not in h.content for h in hits_a)

    assert hits_b
    assert all("workspace B" in h.content for h in hits_b)
    assert all("workspace A" not in h.content for h in hits_b)


@pytest.mark.asyncio
async def test_cannot_access_other_workspace_documents(session_factory):
    seeded = await _seed_two_workspaces(session_factory)
    token_a = create_access_token(seeded["u1_id"])
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/workspaces/{seeded['w2_id']}/documents",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert resp.status_code == 404

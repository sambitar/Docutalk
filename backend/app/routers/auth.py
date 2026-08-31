from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import create_access_token, get_current_user, hash_password, verify_password
from app.models import User, Workspace
from app.schemas import LoginRequest, MeResponse, RegisterRequest, TokenResponse, WorkspaceOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await db.execute(select(User).where(User.email == body.email.lower()))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=body.email.lower(), password_hash=hash_password(body.password))
    db.add(user)
    await db.flush()
    workspace = Workspace(name=f"{body.email.split('@')[0]}'s workspace", owner_user_id=user.id)
    db.add(workspace)
    await db.commit()
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))


me_router = APIRouter(tags=["me"])


@me_router.get("/me", response_model=MeResponse)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> MeResponse:
    result = await db.execute(
        select(User).options(selectinload(User.workspace)).where(User.id == user.id)
    )
    loaded = result.scalar_one()
    if loaded.workspace is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Workspace missing")
    return MeResponse(
        id=loaded.id,
        email=loaded.email,
        workspace=WorkspaceOut.model_validate(loaded.workspace),
    )

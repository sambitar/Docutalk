import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WorkspaceOut(BaseModel):
    id: uuid.UUID
    name: str
    openai_key_last4: str | None
    openai_key_validated_at: datetime | None

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    id: uuid.UUID
    email: str
    workspace: WorkspaceOut


class OpenAIKeyRequest(BaseModel):
    api_key: str = Field(min_length=10, max_length=256)


class OpenAIKeyResponse(BaseModel):
    openai_key_last4: str
    openai_key_validated_at: datetime


class DocumentOut(BaseModel):
    id: uuid.UUID
    title: str
    source_filename: str
    byte_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class ChatSource(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    page: int | None = None
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]


class HealthResponse(BaseModel):
    status: str
    database: str

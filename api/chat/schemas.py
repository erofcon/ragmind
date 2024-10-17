from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

import settings


class Message(BaseModel):
    role: str
    content: str


class MessageCreate(Message):
    pass


class MessageBase(Message):
    id: UUID
    created_at: datetime
    chat_id: UUID

    class Config:
        from_attributes = True


class MSettings(BaseModel):
    temperature: float = 0.1
    top_p: float = 0.3
    max_tokens: int = 512
    presence_penalty: float = 0.4
    frequency_penalty: float = 0.7


class PromptEngine(BaseModel):
    rag_system: str = settings.DEFAULT_RAG_SYSTEM_PROMPT
    system: str = settings.DEFAULT_SYSTEM_PROMPT
    threshold: float = 0.6
    k: int = 10
    user_rerank: bool = True


class ChatModelCreate(BaseModel):
    name: str
    kb_id: UUID
    m_settings: MSettings = MSettings()
    prompt_engine: PromptEngine = PromptEngine()


class ChatModel(ChatModelCreate):
    id: UUID
    created_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True

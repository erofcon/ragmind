import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class KnowledgeBaseBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class KnowledgeBaseCreate(KnowledgeBaseBase):
    chunk_size: int = 1024
    overlap: int = 0
    delimiter: str = r'\n|!|\?|;|。|；|！|？'


class KnowledgeBase(KnowledgeBaseCreate):
    id: uuid.UUID
    doc_count: int
    created_at: datetime

    class Config:
        from_attributes = True

import uuid
from datetime import datetime

from pydantic import BaseModel

from api.document.models import ParsingStatus


class DocumentCreate(BaseModel):
    name: str
    kb_id: uuid.UUID
    file_path: str


class Document(DocumentCreate):
    id: uuid.UUID
    parsing_status: ParsingStatus
    created_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True

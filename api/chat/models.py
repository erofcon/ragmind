import uuid
from datetime import datetime

from sqlalchemy import Table, Column, String, MetaData, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from api.knowledge_base.models import knowledge_base

metadata = MetaData()

chat = Table(
    'chat',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4()),
    Column('name', String(), index=True),
    Column('m_settings', JSONB),
    Column('prompt_engine', JSONB),
    Column('kb_id', UUID(), ForeignKey(knowledge_base.c.id, ondelete='CASCADE')),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow()),
)

message = Table(
    'message',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4()),
    Column('role', String()),
    Column('content', Text()),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow()),
    Column('chat_id', UUID(), ForeignKey(chat.c.id, ondelete='CASCADE')),
)

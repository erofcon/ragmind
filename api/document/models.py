import enum, uuid
from datetime import datetime

from sqlalchemy import MetaData, Table, Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID

from api.knowledge_base.models import knowledge_base

metadata = MetaData()


class ParsingStatus(enum.Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    HAS_ERROR = 'has_error'


document = Table(
    'document',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4()),
    Column('name', String(), index=True),
    Column('file_path', String()),
    Column('parsing_status', Enum(ParsingStatus), default=ParsingStatus.NOT_STARTED),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow()),
    Column('kb_id', UUID(), ForeignKey(knowledge_base.c.id, ondelete='CASCADE')),
)

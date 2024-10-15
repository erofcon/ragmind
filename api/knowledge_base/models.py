import uuid
from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()

knowledge_base = Table(
    'knowledge_base',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4),
    Column('name', String(), unique=True, index=True),
    Column('description', String()),
    Column('doc_count', Integer(), default=0),
    Column('chunk_size', Integer(), default=256),
    Column('overlap', Integer(), default=0),
    Column('delimiter', String(), default=r'\n|!|\?|;|。|；|！|？'),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow()),
)

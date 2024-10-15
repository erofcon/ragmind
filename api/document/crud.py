import os
import shutil
import uuid
from datetime import datetime

from fastapi import File
from sqlalchemy import func

import settings
from api.database import database
from api.document.models import document as doc_db, ParsingStatus
from api.document.schemas import Document
from rag.utils.es_conn import ELASTICSEARCH


async def create_document(kb_id: uuid.UUID, file: File) -> Document:
    file_path = f'{settings.UPLOAD_FILE_PATH}/{kb_id}'
    final_file = f'{file_path}/{file.filename}'

    document = Document(
        id=uuid.uuid4(),
        name=file.filename,
        file_path=final_file,
        parsing_status=ParsingStatus.NOT_STARTED,
        kb_id=kb_id,
        created_at=datetime.utcnow()
    )

    if not os.path.isdir(file_path):
        os.makedirs(file_path)

    with open(final_file, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    query = doc_db.insert().values(
        document.model_dump()
    )

    await database.execute(query)

    return document


async def get_list_document(kb_id: uuid.UUID) -> list[Document]:
    query = doc_db.select().where(doc_db.c.kb_id == kb_id)

    return await database.fetch_all(query)


async def get_count_documents_by_kb_id(kb_id: uuid.UUID) -> int:
    query = doc_db.select().with_only_columns(func.count()).where(doc_db.c.kb_id == kb_id)

    return await database.fetch_val(query)


async def get_detail_document_by_related_kb(kb_id: uuid.UUID, doc_id: uuid.UUID) -> Document:
    query = doc_db.select().where(doc_db.c.id == doc_id and doc_db.c.kb_id == kb_id)

    return await database.fetch_one(query)


async def delete_document(kb_id: uuid.UUID, doc_id: uuid.UUID, file_path: str) -> None:
    query = doc_db.delete().where(doc_db.c.id == doc_id)

    await database.execute(query)

    if os.path.exists(file_path):
        os.remove(file_path)

    try:
        await ELASTICSEARCH.delete_index_chunks(index_name=kb_id, doc_id=doc_id)

    except Exception as e:
        raise e


async def update_document_parsing_status(doc_id: uuid.UUID, parsing_status: ParsingStatus):
    query = doc_db.update().values(
        parsing_status=parsing_status,
    ).where(doc_db.c.id == doc_id)

    return await database.execute(query)

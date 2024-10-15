import typing
import uuid
from datetime import datetime

from api.document.crud import get_count_documents_by_kb_id, get_list_document, delete_document
from api.knowledge_base.schemas import KnowledgeBaseCreate, KnowledgeBase
from api.knowledge_base.models import knowledge_base as kb_db

from api.database import database
from rag.utils.es_conn import ELASTICSEARCH


async def create_knowledge_base(kb_schemas: KnowledgeBaseCreate) -> KnowledgeBase:
    kb = KnowledgeBase(
        **kb_schemas.model_dump(),
        id=uuid.uuid4(),
        doc_count=0,
        created_at=datetime.utcnow(),
    )

    query = kb_db.insert().values(
        kb.model_dump()
    )

    try:
        await ELASTICSEARCH.create_index(index_name=kb.id)

    except Exception as e:
        raise e

    await database.execute(query)

    return kb


async def get_list_knowledge_base() -> KnowledgeBase:
    query = kb_db.select()

    return await database.fetch_all(query)


async def get_knowledge_base_by_id(kb_id: uuid.UUID) -> KnowledgeBase:
    query = kb_db.select().where(kb_db.c.id == kb_id)

    return await database.fetch_one(query)


async def update_knowledge_base_file_count(kb_id: uuid.UUID) -> typing.Any:
    count = await get_count_documents_by_kb_id(kb_id)

    query = kb_db.update().values(
        doc_count=count,
    ).where(kb_db.c.id == kb_id)

    return await database.execute(query)


async def delete_knowledge_base_by_id(kb_id: uuid.UUID) -> typing.Any:
    documents = await get_list_document(kb_id)

    if documents:
        for document in documents:
            await delete_document(kb_id=kb_id, doc_id=document.id, file_path=document.file_path)

    query = kb_db.delete().where(kb_db.c.id == kb_id)

    try:
        await ELASTICSEARCH.delete_index(index_name=kb_id)
    except Exception as e:
        raise e

    return await database.execute(query)


async def update_knowledge_base(kb: KnowledgeBase, kb_create: KnowledgeBaseCreate) -> KnowledgeBaseCreate:
    # TODO: update parsing status if updated chuck size

    updated_kb_data = dict(kb)

    updated_kb = kb_create.model_dump(exclude_unset=True)

    merged_data = {**updated_kb_data, **updated_kb}

    updated_kb_instance = KnowledgeBaseCreate(**merged_data)

    query = kb_db.update().values(
        updated_kb_instance.model_dump(),
    ).where(kb_db.c.id == kb.id)

    await database.execute(query)

    return updated_kb_instance

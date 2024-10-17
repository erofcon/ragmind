import uuid

from fastapi import APIRouter, HTTPException, status

from api.knowledge_base.crud import create_knowledge_base, get_list_knowledge_base, delete_knowledge_base_by_id, \
    get_knowledge_base_by_id, update_knowledge_base
from api.knowledge_base.schemas import KnowledgeBaseCreate, KnowledgeBase

from rag.utils.es_conn import ELASTICSEARCH

router = APIRouter()


@router.post("/api/v1/kb/create")
async def create_kb(kb_create: KnowledgeBaseCreate):
    try:
        return await create_knowledge_base(kb_create)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/api/v1/kb/list', response_model=list[KnowledgeBase])
async def kb_list():
    try:
        return await get_list_knowledge_base()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/api/v1/kb/delete')
async def delete(kb_id: uuid.UUID):
    try:
        await delete_knowledge_base_by_id(kb_id=kb_id)
        return status.HTTP_204_NO_CONTENT

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/api/v1/kb/update')
async def update(kb_id: uuid.UUID, kb_create: KnowledgeBaseCreate):
    # TODO: check document progress
    try:
        kb = await get_knowledge_base_by_id(kb_id=kb_id)

        if not kb:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='knowledge base not found')

        return await update_knowledge_base(kb, kb_create)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/api/v1/kb/search')
async def search(kb_id: uuid.UUID, query: str, user_rerank: bool = True, threshold: float = 0.6, k: int = 10):
    kb = await get_knowledge_base_by_id(kb_id=kb_id)

    if not kb:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='knowledge base not found')

    return await ELASTICSEARCH.hybrid_search(index_name=kb_id, query=query, user_rerank=user_rerank,
                                             threshold=threshold, k=k)

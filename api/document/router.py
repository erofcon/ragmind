import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, status, BackgroundTasks

from api.document.crud import create_document, get_list_document, get_detail_document_by_related_kb, delete_document
from api.document.models import ParsingStatus
from api.document.schemas import Document
from api.knowledge_base.crud import get_knowledge_base_by_id, update_knowledge_base_file_count
from api.document.tasks import chunk_create

from rag.utils.es_conn import ELASTICSEARCH

router = APIRouter()


@router.post('/api/v1/doc/upload')
async def document_upload(kb_id: uuid.UUID, files: list[UploadFile] = File(...)):
    try:
        values = []
        if not await get_knowledge_base_by_id(kb_id=kb_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Knowledge base not exists")

        for file in files:
            record = await create_document(kb_id=kb_id, file=file)
            values.append(record)

        await update_knowledge_base_file_count(kb_id)

        return values

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/api/v1/doc/list', response_model=list[Document])
async def document_list(kb_id: uuid.UUID):
    try:
        if not await get_knowledge_base_by_id(kb_id=kb_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Knowledge base not exists")

        return await get_list_document(kb_id=kb_id)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/api/v1/doc/delete')
async def document_delete(kb_id: uuid.UUID, doc_id: uuid.UUID):
    try:

        document = await get_detail_document_by_related_kb(kb_id=kb_id, doc_id=doc_id)

        if document:
            await delete_document(kb_id=kb_id, doc_id=doc_id, file_path=document.file_path)

            return {'success': True}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document not exists")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/api/v1/doc/create_chunks')
async def document_create_chunks(kb_id: uuid.UUID, doc_id: uuid.UUID, background_tasks: BackgroundTasks):
    kb = await get_knowledge_base_by_id(kb_id=kb_id)
    document = await get_detail_document_by_related_kb(kb_id=kb_id, doc_id=doc_id)

    if not kb:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Knowledge base not exists")

    if not document:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document not exists")

    if document.parsing_status == ParsingStatus.IN_PROGRESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document parsing in progress")

    # TODO: check background worker
    background_tasks.add_task(chunk_create, kb, document)

    return {"Document parsing in progress"}


@router.get('/api/v1/doc/get_chunks')
async def document_get_chunks(kb_id: uuid.UUID, doc_id: uuid.UUID, page: int = 1, page_size: int = 10):
    kb = await get_knowledge_base_by_id(kb_id=kb_id)
    document = await get_detail_document_by_related_kb(kb_id=kb_id, doc_id=doc_id)

    if not kb:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Knowledge base not exists")

    if not document:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document not exists")

    return await ELASTICSEARCH.get_all_document_chunks(index_name=kb_id, doc_id=doc_id, page=page, page_size=page_size)

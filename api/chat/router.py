import uuid

from fastapi import APIRouter, HTTPException, status

from api.chat.schemas import ChatModelCreate, MessageCreate
from api.chat.crud import create_chat, get_chat_list, get_chat_by_id, chat_update, delete_chat, get_all_messages, \
    delete_all_messages
from api.chat.utils.generate import Generate

router = APIRouter()


@router.post('/api/v1/chat/create')
async def chat_create(chat: ChatModelCreate):
    try:
        return await create_chat(chat)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/api/v1/chat/update')
async def update_chat(chat_id: uuid.UUID, chat: ChatModelCreate):
    try:
        chat_base = await get_chat_by_id(chat_id)

        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')

        return await chat_update(chat_base, chat)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/api/v1/chat/delete')
async def chat_delete(chat_id: uuid.UUID):
    try:
        await delete_chat(chat_id)
        return status.HTTP_204_NO_CONTENT

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/api/v1/chat/list')
async def list_chats():
    try:
        return await get_chat_list()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/api/v1/chat/generation')
async def chat_generate(chat_id: uuid.UUID, message: MessageCreate, use_rag: bool = True, extract_keywords: bool = True,
                        stream: bool = True):
    chat = await get_chat_by_id(chat_id)

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')

    generate = Generate(chat=chat)

    return await generate.generate(message=message, user_rag=use_rag, extract_keywords=extract_keywords, stream=stream)


# @router.post('/api/v1/chat/completion')
# async def chat_completion(chat_id: uuid.UUID, message: MessageCreate, use_rag: bool = True,
#                           extract_keywords: bool = True):
#
#
#     if not chat:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')
#
#     await add_message_to_chat(chat_id, message)
#
#     messages = await get_all_messages(chat_id)
#
#     if not use_rag:
#         return StreamingResponse(
#             LLM.stream_chat(chat_id=chat_id, history=messages, system=chat.prompt_engine["system"],
#                             conf=chat.m_settings),
#             media_type="text/plain")
#
#     else:
#         result = await ELASTICSEARCH.hybrid_search(index_name=chat.kb_id, query=message.content,
#                                                    user_rerank=chat.prompt_engine["user_rerank"],
#                                                    threshold=chat.prompt_engine["threshold"], k=chat.prompt_engine["k"])
#
#         prompt = chat.prompt_engine["rag_system"].format(knowledge_base=result)
#         conf = get_model_config(conf=chat.m_settings)
#
#         return StreamingResponse(
#             LLM.stream_chat(chat_id=chat_id, history=messages, system=prompt,
#                             conf=conf),
#             media_type="text/plain")


@router.get('/api/v1/chat/message/list')
async def list_messages(chat_id: uuid.UUID):
    try:
        chat = await get_chat_by_id(chat_id)

        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')

        return await get_all_messages(chat_id)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/api/v1/chat/message/clear')
async def chat_message_clear(chat_id: uuid.UUID):
    try:
        chat = await get_chat_by_id(chat_id)

        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')

        await delete_all_messages(chat_id)

        return status.HTTP_204_NO_CONTENT

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

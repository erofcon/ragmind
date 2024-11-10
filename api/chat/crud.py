import typing
from typing import Optional, Any
from datetime import datetime
import uuid
from api.chat.schemas import ChatModelCreate, ChatModel, MessageCreate, MessageBase, MessageMetadata, Source
from api.chat.models import chat as chat_model
from api.chat.models import message as message_model
from api.database import database


async def create_chat(chat: ChatModelCreate) -> ChatModel:
    chat = ChatModel(**chat.model_dump(), id=uuid.uuid4(), created_at=datetime.utcnow())

    query = chat_model.insert().values(
        chat.model_dump()
    )

    await database.execute(query)

    return chat


async def get_chat_by_id(chat_id: uuid.UUID) -> ChatModel:
    query = chat_model.select().where(chat_model.c.id == chat_id)

    return await database.fetch_one(query)


async def get_chat_list() -> ChatModel:
    query = chat_model.select()

    return await database.fetch_all(query)


async def chat_update(chat: ChatModel, chat_create: ChatModelCreate) -> ChatModelCreate:
    updated_chat_model = dict(chat)
    updated_chat = chat_create.model_dump(exclude_unset=True)
    merged_data = {**updated_chat_model, **updated_chat}
    updated_chat_instance = ChatModelCreate(**merged_data)

    query = chat_model.update().values(
        updated_chat_instance.model_dump()
    ).where(chat_model.c.id == chat.id)

    await database.execute(query)

    return updated_chat_instance


async def delete_chat(chat_id: uuid.UUID) -> typing.Any:
    query = chat_model.delete().where(chat_model.c.id == chat_id)

    return await database.execute(query)


async def delete_all_messages(chat_id: uuid.UUID) -> typing.Any:
    query = message_model.delete().where(message_model.c.chat_id == chat_id)

    return await database.execute(query)


async def get_all_messages(chat_id: uuid.UUID) -> list[MessageBase]:
    query = message_model.select().where(message_model.c.chat_id == chat_id)

    return await database.fetch_all(query)


async def add_message_to_chat(chat_id: uuid.UUID, message: MessageCreate,
                              metadata: Optional[MessageMetadata] = None) -> dict[str, Any]:
    if metadata is None:
        metadata = MessageMetadata()

    m = MessageBase(
        **message.model_dump(),
        id=uuid.uuid4(),
        created_at=datetime.utcnow(),
        chat_id=chat_id,
        metadata=metadata
    )

    serialized_data = m.model_dump(exclude_none=True)

    if isinstance(serialized_data.get("metadata"), dict) and "source" in serialized_data["metadata"]:
        serialized_data["metadata"]["source"] = [
            item.model_dump() if isinstance(item, Source) else item
            for item in serialized_data["metadata"]["source"]
        ]

    query = message_model.insert().values(serialized_data)
    await database.execute(query)

    return serialized_data


async def update_message_content(message_id: uuid.UUID, message: str) -> typing.Any:
    query = message_model.update().where(message_model.c.id == message_id).values(
        content=message
    )

    return await database.execute(query)

import json
import typing
from datetime import datetime
import uuid
from api.chat.schemas import ChatModelCreate, ChatModel, MessageCreate, MessageBase, Message
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


async def add_message_to_chat(chat_id: uuid.UUID, message: MessageCreate) -> MessageBase:
    message = MessageBase(**message.model_dump(), id=uuid.uuid4(), created_at=datetime.utcnow(), chat_id=chat_id)

    query = message_model.insert().values(message.model_dump())

    await database.execute(query)

    return query

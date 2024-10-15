import uuid

from openai import AsyncClient, APIError

import settings
from api.chat.schemas import Message, MessageBase, MSettings, MessageCreate
from api.chat.crud import add_message_to_chat


class DefaultChat:
    _llm: AsyncClient

    def __init__(self):
        self._llm = AsyncClient(base_url=settings.LLM_HOST, api_key=settings.LLM_API_KEY)

    async def check_connection(self):
        try:
            await self._llm.models.list()

        except Exception as e:
            raise e

    def chat(self, system, history, gen_conf):
        pass

    async def stream_chat(self, chat_id: uuid.UUID, history: list[MessageBase], system: str = None,
                          conf: dict = None) -> str:

        messages = [{"role": message.role, "content": message.content} for message in history if
                    message.content != '' or message.role != '']

        options = {}
        if "temperature" in conf: options["temperature"] = conf["temperature"]
        if "max_tokens" in conf: options["max_tokens"] = conf["max_tokens"]
        if "top_p" in conf: options["top_p"] = conf["top_p"]
        if "presence_penalty" in conf: options["presence_penalty"] = conf["presence_penalty"]
        if "frequency_penalty" in conf: options["frequency_penalty"] = conf["frequency_penalty"]

        if system:
            messages.insert(0, {"role": "system", "content": system})

        ans = ""

        response = await self._llm.chat.completions.create(
            model="model-identifier",
            messages=messages,
            stream=True,
            temperature=options["temperature"],
            top_p=options["top_p"],
            max_tokens=options["max_tokens"],
            presence_penalty=options["presence_penalty"],
            frequency_penalty=options["frequency_penalty"]
        )

        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                ans += content
                yield content

        message = MessageCreate(
            role="assistant",
            content=ans,
        )
        await add_message_to_chat(chat_id=chat_id, message=message)


LLM = DefaultChat()

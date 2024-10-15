from openai import AsyncClient

import settings


class DefaultChat:
    _llm: AsyncClient

    def __init__(self):
        self._llm = AsyncClient(base_url=settings.LLM_HOST, api_key=settings.LLM_API_KEY)

    async def check_connection(self):
        try:
            await self._llm.models.list()

        except Exception as e:
            raise e

    async def chat(self, history: list[dict], conf: dict = None) -> str:

        completion = self._llm.chat.completions.create(
            model="model-identifier",
            messages=history,
            stream=False,
            **conf
        )

        result = await completion

        return result.choices[0].message.content

    async def stream_chat(self, history: list[dict], conf: dict = None) -> str:

        response = await self._llm.chat.completions.create(
            model="model-identifier",
            messages=history,
            stream=True,
            **conf
        )

        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content


LLM = DefaultChat()

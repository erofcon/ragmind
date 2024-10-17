import re
import uuid
from typing import AsyncGenerator

from starlette.responses import StreamingResponse

from rag.llm.llm import LLM

from api.chat.utils.keyword import KEYWORDEXTRACTOR
from rag.utils.es_conn import ELASTICSEARCH
from api.chat.schemas import ChatModel, MessageBase, MessageCreate
from api.chat.schemas import MSettings
from api.chat.crud import add_message_to_chat, get_all_messages


class Generate:
    _chat_id: uuid.UUID
    _options: dict
    _index: uuid.UUID
    _user_rerank: bool = True
    _threshold: float = 0.8
    _k: int = 10
    _system_prompt: str = None
    _rag_system_prompt: str = None

    def __init__(self, chat: ChatModel):
        self._chat_id = chat.id
        self._index = chat.kb_id
        self._options = self.get_model_config(chat.m_settings)
        self._user_rerank = chat.prompt_engine.get("user_rerank", True)
        self._threshold = chat.prompt_engine.get("threshold", 0.8)
        self._k = chat.prompt_engine.get("k", 10)
        self._system_prompt = chat.prompt_engine.get("system")
        self._rag_system_prompt = chat.prompt_engine.get("rag_system")

    async def generate(self, message: MessageCreate, user_rag: bool = True, extract_keywords: bool = True,
                       stream: bool = True):
        await add_message_to_chat(chat_id=self._chat_id, message=message)
        messages = await get_all_messages(chat_id=self._chat_id)

        system_prompt = self._system_prompt

        if user_rag:
            content = ""
            data1 = None
            data2 = None
            if extract_keywords:
                extract_keywords_query = await self._get_extract_keywords_query(content=message.content)
                data1 = await self._search_knowledge_base(query=extract_keywords_query)
                print(data1)
                print()
                # content += self._get_contents(data=result)

            data2 = await self._search_knowledge_base(query=message.content)
            print(data2)
            print()
            result = self._merge_data(data1=data1, data2=data2)

            print(result)
            # content = self._get_contents(data=result)
            #
            # content += self._get_contents(data=result)
            #
            # print(content)
        #     system_prompt = self._rag_system_prompt.format(knowledge_base=content)
        #
        # history = self.get_history(messages, system=system_prompt)
        #
        # if stream:
        #     return StreamingResponse(self._stream_response(history), media_type="text/plain")
        #
        # response = await self._respond(history, stream=False)
        # await self._add_response_to_chat(response)
        # return response

    async def _get_extract_keywords_query(self, content: str) -> str:

        keyword = await KEYWORDEXTRACTOR.extract_keywords(question=content, options=self._options)
        pattern = r'ключевые\s*слова[:\s]*([\w,\s]+)'

        match = re.search(pattern, keyword, re.IGNORECASE | re.DOTALL)

        if match:
            return match.group(1).strip().replace('\n', ' ')

        return ""

    # async def _get_query(self, content: str, extract_keywords: bool):
    #     if extract_keywords:
    #         keyword = await KEYWORDEXTRACTOR.extract_keywords(question=content, options=self._options)
    #         pattern = r'ключевые\s*слова[:\s]*([\w,\s]+)'
    #
    #         match = re.search(pattern, keyword, re.IGNORECASE | re.DOTALL)
    #
    #         if match:
    #             return match.group(1).strip().replace('\n', ' ')
    #
    #     return content

    async def _search_knowledge_base(self, query: str):
        return await ELASTICSEARCH.hybrid_search(
            index_name=self._index, query=query,
            user_rerank=self._user_rerank,
            threshold=self._threshold,
            k=self._k
        )

    async def _stream_response(self, history: list[dict]) -> AsyncGenerator[str, None]:
        buffer = []
        async for chunk in LLM.stream_chat(history=history, conf=self._options):
            buffer.append(chunk)
            yield chunk

        full_response = "".join(buffer)
        await self._add_response_to_chat(full_response)

    async def _add_response_to_chat(self, response: str):
        response_message = MessageCreate(
            chat_id=self._chat_id,
            role="assistant",
            content=response
        )
        await add_message_to_chat(chat_id=self._chat_id, message=response_message)

    async def _respond(self, history: list[dict], stream: bool):

        if stream:
            return StreamingResponse(
                LLM.stream_chat(history=history, conf=self._options),
                media_type="text/plain"
            )
        return await LLM.chat(history=history, conf=self._options)

    @classmethod
    def _merge_data(cls, data1: dict, data2: dict, max_records=10):
        combined = {}

        for item in data1:
            combined[item['id']] = item

        for item in data2:
            if item['id'] in combined:

                if item['score'] > combined[item['id']]['score']:
                    combined[item['id']] = item
            else:
                combined[item['id']] = item

        merged_data = sorted(combined.values(), key=lambda x: x['score'], reverse=True)

        return merged_data[:max_records]

    @classmethod
    def _get_contents(cls, data: dict) -> str:
        contents = [item['source']['content'] + "\n\n" for item in data]

        return "".join(contents)

    @classmethod
    def get_history(cls, messages: list[MessageBase], system: str = None):
        msg = [{"role": message.role, "content": message.content}
               for message in messages if message.content or message.role]
        if system:
            msg.insert(0, {"role": "system", "content": system})
        return msg

    @classmethod
    def get_model_config(cls, conf: MSettings):
        return {
            "temperature": conf.get("temperature"),
            "max_tokens": conf.get("max_tokens"),
            "top_p": conf.get("top_p"),
            "presence_penalty": conf.get("presence_penalty"),
            "frequency_penalty": conf.get("frequency_penalty")
        }

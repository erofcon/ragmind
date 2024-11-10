import json
import re
import uuid
from datetime import datetime
from typing import AsyncGenerator, Any, Optional, List

from starlette.responses import StreamingResponse

from rag.llm.llm import LLM

from api.chat.utils.keyword import KEYWORDEXTRACTOR
from rag.utils.es_conn import ELASTICSEARCH
from api.chat.schemas import ChatModel, MessageBase, MessageCreate, MessageMetadata
from api.chat.schemas import MSettings
from api.chat.crud import add_message_to_chat, get_all_messages, \
    update_message_content


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
        self._options = self._get_model_config(chat.m_settings)
        self._user_rerank = chat.prompt_engine.get("user_rerank", True)
        self._threshold = chat.prompt_engine.get("threshold", 0.8)
        self._k = chat.prompt_engine.get("k", 10)
        self._system_prompt = chat.prompt_engine.get("system")
        self._rag_system_prompt = chat.prompt_engine.get("rag_system")

    async def generate(self, message: MessageCreate, user_rag: bool = True, extract_keywords: bool = True,
                       stream: bool = True) -> Any:
        try:
            await add_message_to_chat(chat_id=self._chat_id, message=message)
            messages = await get_all_messages(chat_id=self._chat_id)

            metadata = None
            system_prompt = self._system_prompt

            if user_rag:
                result, metadata = await self._retrieve_relevant_data(message, extract_keywords)
                system_prompt = self._rag_system_prompt.format(knowledge_base=metadata.kb_content)

            history = self._get_history(messages, system=system_prompt)

            if stream:
                return StreamingResponse(self._stream_metadata_and_content(history, metadata=metadata),
                                         media_type="text/plain")

            llm_response = await self._respond(history, stream=False)
            return await self._add_response_to_chat(llm_response=llm_response, metadata=metadata)
        except Exception as e:
            print(f"Error in generate: {e}")
            raise

    async def _retrieve_relevant_data(self, message: MessageCreate, extract_keywords: bool) -> tuple[
        Optional[list[dict]], Optional[MessageMetadata]]:

        try:
            if extract_keywords:

                extract_keywords_query = await self._get_extract_keywords_query(content=message.content)
                data1 = await self._search_knowledge_base(query=extract_keywords_query, rerank_query=message.content)
                data2 = await self._search_knowledge_base(query=message.content)
                result = self._merge_data(data1=data1, data2=data2, max_records=self._k)
            else:

                result = await self._search_knowledge_base(query=message.content)

            metadata = self._get_metadata(result)
            return result, metadata
        except Exception as e:
            print(f"Error in _retrieve_relevant_data: {e}")
            return None, None

    async def _get_extract_keywords_query(self, content: str) -> str:
        try:
            keyword = await KEYWORDEXTRACTOR.extract_keywords(question=content, options=self._options)
            match = re.search(r'ключевые\s*слова[:\s]*([\w,\s]+)', keyword, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip().replace('\n', ' ') if match else content
        except Exception as e:
            print(f"Error in _get_extract_keywords_query: {e}")
            return content

    async def _search_knowledge_base(self, query: str, rerank_query: Optional[str] = None) -> List[dict]:
        try:
            return await ELASTICSEARCH.hybrid_search(
                index_name=self._index, query=query,
                user_rerank=self._user_rerank,
                rerank_query=rerank_query,
                threshold=self._threshold,
                k=self._k
            )
        except Exception as e:
            print(f"Error in _search_knowledge_base: {e}")
            return []

    async def _stream_metadata_and_content(self, history: List[dict], metadata: Optional[MessageMetadata]) -> \
            AsyncGenerator[str, None]:
        try:
            message = await self._add_response_to_chat(llm_response="", metadata=metadata)
            serialized_message = self._serialize_data(message)

            yield json.dumps(serialized_message, ensure_ascii=False) + "\n"

            full_response = ""
            async for chunk in LLM.stream_chat(history=history, conf=self._options):
                full_response += chunk
                await update_message_content(message_id=message['id'], message=full_response)
                yield chunk + "\n"
        except Exception as e:
            print(f"Error in _stream_metadata_and_content: {e}")
            yield json.dumps({"error": "Stream interrupted due to an error"}, ensure_ascii=False) + "\n"

    async def _add_response_to_chat(self, llm_response: str, metadata: Optional[MessageMetadata]) -> dict[str, Any]:
        try:
            message = MessageCreate(chat_id=self._chat_id, role="assistant", content=llm_response)
            return await add_message_to_chat(chat_id=self._chat_id, message=message, metadata=metadata)
        except Exception as e:
            print(f"Error in _add_response_to_chat: {e}")
            return {}

    async def _respond(self, history: List[dict], stream: bool) -> Any:
        try:
            if stream:
                return StreamingResponse(LLM.stream_chat(history=history, conf=self._options), media_type="text/plain")
            return await LLM.chat(history=history, conf=self._options)
        except Exception as e:
            print(f"Error in _respond: {e}")
            return {}

    @classmethod
    def _merge_data(cls, data1: List[dict], data2: List[dict], max_records=10) -> List[dict]:
        combined = {item['id']: item for item in data1}
        for item in data2:
            if item['id'] not in combined or item['score'] > combined[item['id']]['score']:
                combined[item['id']] = item
        return sorted(combined.values(), key=lambda x: x['score'], reverse=True)[:max_records]

    @classmethod
    def _get_metadata(cls, data: List[dict]) -> MessageMetadata:
        try:
            unique_sources = set()
            contents, sources = [], []

            for item in data:
                source_id, source_name, source_content = item['source']['doc_id'], item['source']['title'], \
                    item['source']['content'] + "\n\n"
                if (source_id, source_name) not in unique_sources:
                    unique_sources.add((source_id, source_name))
                    sources.append({'id': source_id, 'name': source_name})
                contents.append(source_content)

            metadata = MessageMetadata()
            metadata.kb_content = "".join(contents)
            metadata.source = sources
            return metadata
        except Exception as e:
            print(f"Error in _get_metadata: {e}")
            return MessageMetadata()

    @classmethod
    def _get_history(cls, messages: List[MessageBase], system: Optional[str] = None) -> List[dict]:
        history = [{"role": message.role, "content": message.content} for message in messages if
                   message.content or message.role]
        if system:
            history.insert(0, {"role": "system", "content": system})
        return history

    @classmethod
    def _get_model_config(cls, conf: MSettings) -> dict:
        return {
            "temperature": conf.get("temperature"),
            "max_tokens": conf.get("max_tokens"),
            "top_p": conf.get("top_p"),
            "presence_penalty": conf.get("presence_penalty"),
            "frequency_penalty": conf.get("frequency_penalty")
        }

    @staticmethod
    def _serialize_data(data: dict) -> dict:
        return {
            key: str(value) if isinstance(value, (uuid.UUID, datetime)) else value
            for key, value in data.items()
        }

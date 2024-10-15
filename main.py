from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.knowledge_base.router import router as knowledge_base_router
from api.document.router import router as document_router
from api.chat.router import router as chat_router
from api.database import database

from rag.utils.es_conn import ELASTICSEARCH
from rag.llm.embedding_model import EMBEDDING_MODEL
from rag.llm.rerank_model import RERANK_MODEL
from rag.llm.llm import LLM


@asynccontextmanager
async def lifespan(_: FastAPI):
    await database.connect()

    await LLM.check_connection()
    await ELASTICSEARCH.connection()
    EMBEDDING_MODEL.connection()
    RERANK_MODEL.connection()

    yield

    await ELASTICSEARCH.close_connection()
    await database.disconnect()


app = FastAPI(title='RagMind', lifespan=lifespan)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"], )

app.include_router(knowledge_base_router)

app.include_router(document_router)
app.include_router(chat_router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='127.0.0.1', port=8000, reload=True
    )

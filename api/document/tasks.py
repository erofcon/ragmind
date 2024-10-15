import os

from api.document.crud import update_document_parsing_status
from api.document.models import ParsingStatus
from api.document.schemas import Document
from api.knowledge_base.schemas import KnowledgeBase
from doc_parser.parser.txt_parser import TxtParser
from rag.utils.es_conn import ELASTICSEARCH


async def chunk_create(kb: KnowledgeBase, document: Document):
    try:
        await update_document_parsing_status(doc_id=document.id, parsing_status=ParsingStatus.IN_PROGRESS)
        if os.path.exists(document.file_path):
            with open(document.file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                res = TxtParser.parser_txt(text=text, chunk_size=kb.chunk_size, overlap=kb.overlap,
                                           delimiter=rf'{kb.delimiter}')

                await ELASTICSEARCH.upsert_to_index(index_name=kb.id, doc_id=document.id, title=document.name,
                                                    chunks=res)

                await update_document_parsing_status(doc_id=document.id, parsing_status=ParsingStatus.COMPLETED)
    except Exception as e:
        # TODO: error add to log

        print(e)
        await update_document_parsing_status(doc_id=document.id, parsing_status=ParsingStatus.HAS_ERROR)

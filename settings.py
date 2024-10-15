UPLOAD_FILE_PATH = 'upload_files'
ELASTICSEARCH_HOST = 'http://localhost:9200'
ELASTICSEARCH_USERNAME = ''
ELASTICSEARCH_PASSWORD = ''
DIMENSION = 768
LLM_HOST = 'http://localhost:1234/v1'
LLM_API_KEY = 'lm-studio'
EMBEDDING_MODEL_DIR = 'huggingface/BAAI/bge-m3'
RERANKER_MODEL_DIR = 'huggingface/BAAI/bge-reranker-v2-m3'
DEFAULT_RAG_SYSTEM_PROMPT = """
Вы умный помощник.
Пожалуйста, кратко изложите содержание базы знаний, чтобы ответить на вопрос.
Пожалуйста, укажите данные в базе знаний и ответьте подробно. 
Если все содержимое базы знаний не имеет отношения к вопросу, ваш ответ должен включать предложение 
«Ответ, который вы ищете, не найден в базе знаний!» 
Ответы должны учитывать историю чата.
Вот база знаний:

      {knowledge_base}
      
Вышеуказанное является базой знаний.

"""

DEFAULT_SYSTEM_PROMPT = """
Вы умный помощник.
Пожалуйста, отвечайте только на русском языке.
Ответы должны учитывать историю чата.
"""

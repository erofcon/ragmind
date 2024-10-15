from rag.llm.llm import LLM

import settings


class KeywordExtract:
    _prompt: str

    def __init__(self, prompt: str = None):

        if prompt:
            self._prompt = prompt
        else:
            self._prompt = settings.DEFAULT_KEYWORD_EXTRACTOR_PROMPT

    async def extract_keywords(self, question: str, top_n: int = 5, options: dict = None):
        message = [
            {"role": "system", "content": self._prompt.format(top_n=top_n)},
            {"role": "user", "content": question}]

        return await LLM.chat(history=message, conf=options)


KEYWORDEXTRACTOR = KeywordExtract()

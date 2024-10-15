import torch

from FlagEmbedding import FlagReranker

import settings


class DefaultRerank:
    _model_dir: str
    _model: FlagReranker | None = None

    def __init__(self):
        self._model_dir = settings.RERANKER_MODEL_DIR

    def connection(self):
        self._model = FlagReranker(self._model_dir, use_fp16=torch.cuda.is_available())

    def similarity(self, query: str, texts: list):
        pairs = [(query, t) for t in texts]

        scores = self._model.compute_score(pairs, normalize=True)

        results = [(text, score) for text, score in zip(texts, scores)]

        return results


RERANK_MODEL = DefaultRerank()

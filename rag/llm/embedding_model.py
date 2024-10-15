import torch
from FlagEmbedding import FlagModel

import settings


class DefaultEmbedding:
    _model_dir: str
    _model: FlagModel | None = None

    def __init__(self):
        self._model_dir = settings.EMBEDDING_MODEL_DIR

    def connection(self):
        self._model = FlagModel(self._model_dir, use_fp16=torch.cuda.is_available())

    def encode(self, text: str):
        return self._model.encode_queries([text]).tolist()[0]

    def get_embedding_dims(self, text: str = 'check'):
        embedding = self.encode(text)
        return len(embedding)


EMBEDDING_MODEL = DefaultEmbedding()

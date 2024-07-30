from enum import Enum

from .base_embedding_model import EmbeddingModel
from .sentence_transformer import SentenceTransformerEmbeddingModel, SentenceTransformerModelName


class EmbeddingModelType(str, Enum):
    SENTENCE_TRANSFORMER = "sentence_transformer"


class EmbeddingModelFactory:
    @staticmethod
    def create(embedding_model_type: EmbeddingModelType, *args, **kwargs) -> EmbeddingModel:
        if embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER:
            return SentenceTransformerEmbeddingModel(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported embedding model type: {embedding_model_type}")

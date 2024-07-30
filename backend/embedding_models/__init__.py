from enum import Enum

from .base_embedding_model import EmbeddingModel, EmbeddingModelConfig
from .sentence_transformer import (
    SentenceTransformerEmbeddingModel,
    SentenceTransformerEmbeddingModelConfig,
    SentenceTransformerModelName,
)


class EmbeddingModelType(str, Enum):
    SENTENCE_TRANSFORMER = "sentence_transformer"


class EmbeddingModelFactory:
    @staticmethod
    def create(embedding_model_type: EmbeddingModelType, *args, **kwargs) -> EmbeddingModel:
        if embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER:
            assert embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER
            return SentenceTransformerEmbeddingModel(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported embedding model type: {embedding_model_type}")

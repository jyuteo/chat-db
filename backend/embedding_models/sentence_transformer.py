from enum import Enum
from sentence_transformers import SentenceTransformer

from embedding_models import EmbeddingModel
from logger import get_logger

logger = get_logger()


class SentenceTransformerModelName(str, Enum):
    ALL_MPNET_BASE_768 = "all-mpnet-base-v2"
    ALL_MINILM_L12_384 = "all-MiniLM-L12-v2"
    ALL_MINILM_L6_384 = "all-MiniLM-L6-v2"


class SentenceTransformerEmbeddingModel(EmbeddingModel):
    def __init__(
        self,
        model_name: SentenceTransformerModelName = SentenceTransformerModelName.ALL_MINILM_L12_384,
    ):
        self._model_name = model_name

        logger.info(f"Downloading and loading embedding model {self._model_name}...")
        self._embedding_model = SentenceTransformer(self._model_name, trust_remote_code=True)

        self._embedding_dim = self._embedding_model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded with dimension: {self._embedding_dim}")

    @property
    def model_name(self):
        return self._model_name

    @property
    def embedding_dim(self):
        return self._embedding_dim

    def get_embedding(self, text: str):
        logger.debug(f"Getting embedding for text: {text}")
        embedding = self._embedding_model.encode(text)
        return embedding.tolist()

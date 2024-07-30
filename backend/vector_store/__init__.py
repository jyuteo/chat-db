from enum import Enum

from .base_handler import VectorStoreHandler, VectorStoreConfig, DBTableInfo, QuestionSQL
from .tidb import TiDBVectorStoreHandler, TiDBVectorStoreConfig


class VectorStoreType(str, Enum):
    TIDB = "tidb"


class VectorStoreHandlerFactory:
    @staticmethod
    def create(vector_store_type: VectorStoreType, vector_store_config: VectorStoreConfig) -> VectorStoreHandler:
        if vector_store_type == VectorStoreType.TIDB:
            assert isinstance(vector_store_config, TiDBVectorStoreConfig)
            return TiDBVectorStoreHandler(vector_store_config)
        else:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")

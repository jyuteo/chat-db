from enum import Enum

from .base_handler import VectorStoreHandler, DBTableInfo, QuestionSQL
from .tidb import TiDBVectorStoreHandler


class VectorStoreType(str, Enum):
    TIDB = "tidb"


class VectorStoreHandlerFactory:
    @staticmethod
    def create(vector_store_type: VectorStoreType, *args, **kwargs) -> VectorStoreHandler:
        if vector_store_type == VectorStoreType.TIDB:
            return TiDBVectorStoreHandler(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")

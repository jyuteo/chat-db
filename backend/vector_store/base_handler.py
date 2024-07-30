from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Dict


@dataclass
class DBTableInfo:
    id: int = None
    database_name: str = None
    table_name: str = None
    table_schema: str = None
    table_schema_embedding: List[float] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class QuestionSQL:
    id: int = None
    database_name: str = None
    table_name: str = None
    question: str = None
    question_embedding: List[float] = None
    sql: str = None
    metadatas: Dict = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class VectorStoreConfig:
    embedding_model_name: str = None
    embedding_model_dim: int = None


class VectorStoreHandler(ABC):
    @abstractmethod
    def insert_db_table_info(self, data: List[DBTableInfo]):
        pass

    @abstractmethod
    def get_db_table_info_by_database_name_and_table_name(
        self, database_name: str, table_name: str
    ) -> List[DBTableInfo]:
        pass

    @abstractmethod
    def insert_question_sql_pairs(self, data: List[QuestionSQL]):
        pass

    @abstractmethod
    def get_top_k_similar_question_sql_pairs_with_question_embedding(
        self,
        query_embedding: List[float],
        k: int = 3,
        min_similarity: float = 0.8,
        filters: Dict = None,
    ) -> List[Tuple[QuestionSQL, float]]:
        pass

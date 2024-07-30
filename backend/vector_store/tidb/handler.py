from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vector_store import VectorStoreHandler, VectorStoreConfig, DBTableInfo, QuestionSQL
from vector_store.tidb.models import (
    Base,
    create_db_table_info_model,
    create_question_sql_model,
)
from vector_store.tidb.utils import convert_sqlalchemy_model_to_dataclass
from db_client import DBType
from logger import get_logger

logger = get_logger()


@dataclass
class TiDBVectorStoreConfig(VectorStoreConfig):
    db_connection_string: str = None
    db_type: DBType = None
    reset_db: bool = False


class TiDBVectorStoreHandler(VectorStoreHandler):
    def __init__(
        self,
        config: TiDBVectorStoreConfig,
    ):
        self.engine = create_engine(config.db_connection_string)
        self.sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        self.DBTableInfoModel = create_db_table_info_model(
            config.db_type, config.embedding_model_name, config.embedding_model_dim
        )
        self.QuestionSQLModel = create_question_sql_model(
            config.db_type, config.embedding_model_name, config.embedding_model_dim
        )

        if config.reset_db:
            logger.warning("Recreating tidb vector store...")
            Base.metadata.drop_all(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
        else:
            Base.metadata.create_all(bind=self.engine)

    def insert_db_table_info(self, data: List[DBTableInfo]):
        with self.sessionmaker() as db:
            for d in data:
                db.add(self.DBTableInfoModel(**asdict(d)))
            db.commit()

    def get_db_table_info_by_database_name_and_table_name(
        self, database_name: str, table_name: str
    ) -> List[DBTableInfo]:
        with self.sessionmaker() as db:
            data = (
                db.query(self.DBTableInfoModel)
                .filter(
                    self.DBTableInfoModel.database_name == database_name, self.DBTableInfoModel.table_name == table_name
                )
                .all()
            )
        result = []
        for d in data:
            result.append(convert_sqlalchemy_model_to_dataclass(d, DBTableInfo))
        return result

    def get_top_k_similar_db_table_info_with_table_schema_embedding(
        self, query_embedding: List[float], k: int = 3, min_similarity: float = 0.8
    ) -> List[Tuple[DBTableInfo, float]]:
        max_distance = 1 - min_similarity
        with self.sessionmaker() as db:
            distance = self.DBTableInfoModel.table_schema_embedding.cosine_distance(query_embedding).label("distance")
            data = (
                db.query(self.DBTableInfoModel, distance)
                .filter(distance <= max_distance)
                .order_by(distance)
                .limit(k)
                .all()
            )
        result = []
        for d, distance in data:
            result.append((convert_sqlalchemy_model_to_dataclass(d, DBTableInfo), 1 - distance))
        return result

    def insert_question_sql_pairs(self, data: List[QuestionSQL]):
        with self.sessionmaker() as db:
            for d in data:
                db.add(self.QuestionSQLModel(**asdict(d)))
            db.commit()

    def get_top_k_similar_question_sql_pairs_with_question_embedding(
        self,
        query_embedding: List[float],
        k: int = 3,
        min_similarity: float = 0.8,
        filters: Dict = None,
    ) -> List[Tuple[QuestionSQL, float]]:
        max_distance = 1 - min_similarity
        with self.sessionmaker() as db:
            distance = self.QuestionSQLModel.question_embedding.cosine_distance(query_embedding).label("distance")
            query = db.query(self.QuestionSQLModel, distance)
            if filters:
                for key, value in filters.items():
                    if hasattr(self.QuestionSQLModel, key):
                        query = query.filter(getattr(self.QuestionSQLModel, key) == value)
            query = query.filter(distance <= max_distance).order_by(distance).limit(k)
            data = query.all()
        result = []
        for d, distance in data:
            result.append((convert_sqlalchemy_model_to_dataclass(d, QuestionSQL), 1 - distance))
        return result

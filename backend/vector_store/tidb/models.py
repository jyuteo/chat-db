import sqlalchemy

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from tidb_vector.sqlalchemy import VectorType

Base = declarative_base()


def create_db_table_info_model(
    db_type: str, embedding_model_type: str, embedding_model_name: str, embedding_model_dim: int
):
    class DBTableInfoModel(Base):
        __tablename__ = f"db_table_info_{db_type}_{embedding_model_type}_{embedding_model_name}"
        __table_args__ = {"extend_existing": True}

        id = Column(Integer, primary_key=True, autoincrement=True)
        database_name = Column(String(255), nullable=False)
        table_name = Column(String(255), nullable=False)
        table_schema = Column(Text, nullable=False)
        table_schema_embedding = Column(
            VectorType(embedding_model_dim), comment="hnsw(distance=cosine)", nullable=False
        )
        created_at = Column(DateTime, server_default=sqlalchemy.text("CURRENT_TIMESTAMP"))
        updated_at = Column(
            sqlalchemy.DateTime,
            server_default=sqlalchemy.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        )

        __table_args__ = (
            UniqueConstraint(
                "database_name",
                "table_name",
                name="uk_database_name_table_name",
            ),
            {"extend_existing": True},
        )

    return DBTableInfoModel


def create_question_sql_model(
    db_type: str, embedding_model_type: str, embedding_model_name: str, embedding_model_dim: int
):
    class QuestionSQLModel(Base):
        __tablename__ = f"question_sql_{db_type}_{embedding_model_type}_{embedding_model_name}"
        __table_args__ = {"extend_existing": True}

        id = Column(Integer, primary_key=True, autoincrement=True)
        database_name = Column(String(255), nullable=True)
        table_name = Column(String(255), nullable=True)
        question = Column(Text, nullable=False)
        question_embedding = Column(VectorType(embedding_model_dim), comment="hnsw(distance=cosine)", nullable=False)
        sql = Column(Text, nullable=False)
        metadatas = Column(sqlalchemy.JSON, nullable=True)
        created_at = Column(DateTime, server_default=sqlalchemy.text("CURRENT_TIMESTAMP"))
        updated_at = Column(
            sqlalchemy.DateTime,
            server_default=sqlalchemy.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        )

    return QuestionSQLModel

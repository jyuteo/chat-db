import sys
import json

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from db_client import DBType
from embedding_models import (
    EmbeddingModelType,
    SentenceTransformerEmbeddingModelConfig,
    SentenceTransformerEmbeddingModel,
)
from vector_store import VectorStoreType, TiDBVectorStoreConfig, TiDBVectorStoreHandler, DBTableInfo, QuestionSQL


def main(
    db_type: DBType, embedding_model_type: EmbeddingModelType, vector_store_type: VectorStoreType, json_data_path: str
):
    db_type = db_type

    embedding_model_type = EmbeddingModelType.SENTENCE_TRANSFORMER
    if embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER:
        embedding_model = SentenceTransformerEmbeddingModel(SentenceTransformerEmbeddingModelConfig())
    else:
        raise ValueError(f"Unsupported embedding model type: {embedding_model_type}")

    vector_store_type = VectorStoreType.TIDB
    if vector_store_type == VectorStoreType.TIDB:
        vector_store_config = TiDBVectorStoreConfig(
            db_type=db_type,
            embedding_model_name=embedding_model.model_name,
            embedding_model_dim=embedding_model.embedding_dim,
        )
        vector_store_handler = TiDBVectorStoreHandler(vector_store_config)
    else:
        raise ValueError(f"Unsupported vector store type: {vector_store_type}")

    with open(json_data_path, "r") as f:
        json_data = json.load(f)

        for group in json_data:
            database = group["database_name"]
            table = group["table_name"]
            schema = group["schema"]

            if database and table and schema:
                db_table_info = DBTableInfo(
                    database=database,
                    table=table,
                    schema=schema,
                    schema_embedding=embedding_model.get_embedding(schema),
                )
                vector_store_handler.add_db_table_info(db_table_info)

            question_sql_pairs = group["question_sql_pairs"]
            for question_sql_pair in question_sql_pairs:
                question_sql = QuestionSQL(
                    question=question_sql_pair["question"],
                    sql=question_sql_pair["sql"],
                    question_embedding=embedding_model.get_embedding(question_sql_pair["question"]),
                )
                vector_store_handler.add_question_sql(question_sql)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--db_type", type=str, default="mysql")
    parser.add_argument("--embedding_model_type", type=str, default="sentence_transformer")
    parser.add_argument("--vector_store_type", type=str, default="tidb")
    parser.add_argument("--json_data_path", type=str)
    args = parser.parse_args()

    main(
        db_type=DBType(args.db_type),
        embedding_model_type=EmbeddingModelType(args.embedding_model_type),
        vector_store_type=VectorStoreType(args.vector_store_type),
        json_data_path=args.json_data_path,
    )

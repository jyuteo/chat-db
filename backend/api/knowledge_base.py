import traceback
from typing import Dict
from flask import Blueprint, session, jsonify, request
from marshmallow import ValidationError

from db_client import DBType
from embedding_models import (
    EmbeddingModelType,
    SentenceTransformerEmbeddingModelConfig,
    SentenceTransformerEmbeddingModel,
)
from vector_store import VectorStoreType, TiDBVectorStoreConfig, TiDBVectorStoreHandler, DBTableInfo, QuestionSQL
from api.request_schemas import AddDBTableInfoSchema, AddQuestionSQLPairsSchema
from logger import get_logger

logger = get_logger()

knowledge_base = Blueprint("knowledge_base", __name__, url_prefix="/knowledge_base")


@knowledge_base.route("/add_db_table_schemas", methods=["POST"])
def add_db_table_schemas():
    schema = AddDBTableInfoSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error:": f"failed to parse request for add_db_table_schemas - {err.messages}"}), 400

    db_type = data["db_type"]
    embedding_model_type = data["embedding_model_type"]
    vector_store_type = data["vector_store_type"]
    db_table_list = data["data"]

    embedding_model = None
    if embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER:
        embedding_model = SentenceTransformerEmbeddingModel(SentenceTransformerEmbeddingModelConfig())
    else:
        e = ValueError(f"Unsupported embedding model type: {embedding_model_type}")
        return jsonify({"error": str(e)}), 400

    vector_store_handler = None
    if vector_store_type == VectorStoreType.TIDB:
        vector_store_config = TiDBVectorStoreConfig(
            db_type=db_type,
            embedding_model_type=embedding_model_type,
            embedding_model_name=embedding_model.model_name,
            embedding_model_dim=embedding_model.embedding_dim,
        )
        vector_store_handler = TiDBVectorStoreHandler(vector_store_config)
    else:
        e = ValueError(f"Unsupported vector store type: {vector_store_type}")
        return jsonify({"error": str(e)}), 400

    try:
        db_table_info_list = list()
        for data in db_table_list:
            db_table_info_list.append(
                DBTableInfo(
                    database_name=data["database_name"],
                    table_name=data["table_name"],
                    table_schema=data["table_schema"],
                    table_schema_embedding=embedding_model.get_embedding(data["table_schema"]),
                )
            )
        vector_store_handler.insert_db_table_info(db_table_info_list)
        return jsonify({"message": "Added db table info successfully."}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@knowledge_base.route("/add_question_sql_pairs", methods=["POST"])
def add_question_sql_pairs():
    schema = AddQuestionSQLPairsSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error:": f"failed to parse request for add_question_sql_pairs - {err.messages}"}), 400

    db_type = data["db_type"]
    embedding_model_type = data["embedding_model_type"]
    vector_store_type = data["vector_store_type"]
    question_sql_pair_list = data["data"]

    embedding_model = None
    if embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER:
        embedding_model = SentenceTransformerEmbeddingModel(SentenceTransformerEmbeddingModelConfig())
    else:
        e = ValueError(f"Unsupported embedding model type: {embedding_model_type}")
        return jsonify({"error": str(e)}), 400

    vector_store_handler = None
    if vector_store_type == VectorStoreType.TIDB:
        vector_store_config = TiDBVectorStoreConfig(
            db_type=db_type,
            embedding_model_type=embedding_model_type,
            embedding_model_name=embedding_model.model_name,
            embedding_model_dim=embedding_model.embedding_dim,
        )
        vector_store_handler = TiDBVectorStoreHandler(vector_store_config)
    else:
        e = ValueError(f"Unsupported vector store type: {vector_store_type}")
        return jsonify({"error": str(e)}), 400

    try:
        question_sql_list = list()
        for data in question_sql_pair_list:
            if ("database_name" in data and "table_name" not in data) or (
                "table_name" in data and "database_name" not in data
            ):
                e = ValueError(f"Field database_name and table_name must be provided together")
                return jsonify({"error": str(e)}), 400

            database_name, table_name = None, None
            if "database_name" in data and "table_name" in data:
                database_name, table_name = data["database_name"], data["table_name"]
                if not vector_store_handler.get_db_table_info_by_database_name_and_table_name(
                    database_name, table_name
                ):
                    e = ValueError(
                        f"Table schema for database_name and table_name provided does not exists. Please add the schema with /knowledge_base/add_db_table_schemas first."
                    )  # noqa: E501 line too long
                    return jsonify({"error": str(e)}), 400

            question_sql_list.append(
                QuestionSQL(
                    database_name=database_name,
                    table_name=table_name,
                    question=data["question"],
                    question_embedding=embedding_model.get_embedding(data["question"]),
                    sql=data["sql"],
                    metadatas=data.get("metadatas", None),
                )
            )
        vector_store_handler.insert_question_sql_pairs(question_sql_list)
        return jsonify({"message": "Added question sql pairs successfully."}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

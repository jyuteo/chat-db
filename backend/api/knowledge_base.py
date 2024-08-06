import traceback
from dataclasses import asdict
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

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
        error = {"msg": f"failed to parse request for add_db_table_schemas - {err.messages}", "trace": None}
        logger.error(error)
        return (jsonify(error), 400)

    db_type = data["db_type"]
    embedding_model_type = data["embedding_model_type"]
    vector_store_type = data["vector_store_type"]
    db_table_list = data["data"]

    embedding_model = None
    if embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER:
        embedding_model = SentenceTransformerEmbeddingModel(SentenceTransformerEmbeddingModelConfig())
    else:
        e = ValueError(f"Unsupported embedding model type: {embedding_model_type}")
        return jsonify({"msg": str(e), "trace": None}), 400

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
        return jsonify({"error": str(e), "trace": None}), 400

    try:
        db_table_info_list = list()
        for data in db_table_list:
            db_table_info_list.append(
                DBTableInfo(
                    database_name=data["database_name"],
                    table_name=data["table_name"],
                    table_schema=data["table_schema"],
                    table_schema_embedding=embedding_model.get_embedding(data["table_schema"]),
                    owner=data.get("owner", None),
                )
            )
        vector_store_handler.insert_db_table_info(db_table_info_list)
        return jsonify({"message": "added db table info successfully."}), 200
    except Exception:
        error = {"msg": "failed to add db table info", "trace": traceback.format_exc()}
        logger.error(error)
        return jsonify(error), 500


@knowledge_base.route("/add_question_sql_pairs", methods=["POST"])
def add_question_sql_pairs():
    schema = AddQuestionSQLPairsSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        error = {"msg": f"failed to parse request for add_question_sql_pairs - {err.messages}", "trace": None}
        logger.error(error)
        return (
            jsonify(error),
            400,
        )

    db_type = data["db_type"]
    embedding_model_type = data["embedding_model_type"]
    vector_store_type = data["vector_store_type"]
    question_sql_pair_list = data["data"]

    embedding_model = None
    if embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER:
        embedding_model = SentenceTransformerEmbeddingModel(SentenceTransformerEmbeddingModelConfig())
    else:
        e = ValueError(f"unsupported embedding model type: {embedding_model_type}")
        logger.error(str(e))
        return jsonify({"msg": str(e), "trace": None}), 400

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
        logger.error(str(e))
        return jsonify({"msg": str(e), "trace": None}), 400

    try:
        question_sql_list = list()
        for data in question_sql_pair_list:
            if ("database_name" in data and "table_name" not in data) or (
                "table_name" in data and "database_name" not in data
            ):
                e = ValueError("Field database_name and table_name must be provided together")
                logger.error(str(e))
                return jsonify({"msg": str(e), "trace": None}), 400

            database_name, table_name = None, None
            if "database_name" in data and "table_name" in data:
                database_name, table_name = data["database_name"], data["table_name"]
                if (
                    database_name
                    and table_name
                    and not vector_store_handler.get_db_table_info_by_database_name_and_table_name(
                        database_name, table_name
                    )
                ):
                    e = ValueError(
                        "Table schema for database_name and table_name provided does not exists. Please add the schema with /knowledge_base/add_db_table_schemas first."  # noqa: E501 line too long
                    )
                    logger.error(str(e))
                    return jsonify({"msg": str(e), "trace": None}), 400

            question_sql_list.append(
                QuestionSQL(
                    database_name=database_name,
                    table_name=table_name,
                    question=data["question"],
                    question_embedding=embedding_model.get_embedding(data["question"]),
                    sql=data["sql"],
                    metadatas=data.get("metadatas", None),
                    owner=data.get("owner", None),
                )
            )
        vector_store_handler.insert_question_sql_pairs(question_sql_list)
        return jsonify({"message": "added question sql pairs successfully."}), 200
    except Exception:
        error = {"msg": "failed to add question sql pairs", "trace": traceback.format_exc()}
        logger.error(error)
        return jsonify(error), 500


@knowledge_base.route("/get", methods=["GET"])
def get_user_knowledge_base():
    user_id = request.args.get("user_id", "")

    embedding_model_type = "sentence_transformer"
    embedding_model = None
    if embedding_model_type == EmbeddingModelType.SENTENCE_TRANSFORMER:
        embedding_model = SentenceTransformerEmbeddingModel(SentenceTransformerEmbeddingModelConfig())
    else:
        e = ValueError(f"Unsupported embedding model type: {embedding_model_type}")
        return jsonify({"msg": str(e), "trace": None}), 400

    vector_store_handler = None
    vector_store_type = "tidb"
    db_type = "mysql"
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
        return jsonify({"msg": str(e), "trace": None}), 400

    try:
        filter = {"owner": user_id} if user_id else {"owner": "public"}
        db_table_info = vector_store_handler.get_db_table_info(filters=filter)
        db_table_info.append(DBTableInfo())
        for info in db_table_info:
            info.table_schema_embedding = None

        sql_data = [None] * len(db_table_info)
        for i, info in enumerate(db_table_info):
            filter = {"owner": user_id} if user_id else {"owner": "public"}
            if info.database_name and info.table_name:
                filter["database_name"] = info.database_name
                filter["table_name"] = info.table_name
            question_sql_pair = vector_store_handler.get_question_sql_pairs(filters=filter)
            for p in question_sql_pair:
                p.question_embedding = None
            sql_data[i] = [asdict(p) for p in question_sql_pair]

        db_table_info = [asdict(d) for d in db_table_info]
        return (
            jsonify(
                {"result": [{"db_table_info": d, "sql_question_pair": p} for d, p in zip(db_table_info, sql_data)]}
            ),
            200,
        )
    except Exception:
        error = {"msg": "failed to get knowledge base", "trace": traceback.format_exc()}
        logger.error(error)
        return jsonify(error), 500

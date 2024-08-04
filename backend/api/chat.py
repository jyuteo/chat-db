import uuid
import traceback

from flask import Blueprint, session, jsonify, request
from marshmallow import ValidationError

from embedding_models import EmbeddingModelType, SentenceTransformerEmbeddingModelConfig
from vector_store import VectorStoreType
from db_client import DBType, MySQLConnConfig
from llm import LLMType, GeminiLLMClientConfig
from chat_handler import ChatHandler, MySQLChatHandler, ChatResponse
from api.request_schemas import CreateChatSessionSchema, SendMessageSchema
from logger import get_logger

logger = get_logger()

chat = Blueprint("chat", __name__, url_prefix="/chat")

CHAT_SESSION_CACHE = dict()


@chat.route("/create", methods=["POST"])
def create_chat_session():
    schema = CreateChatSessionSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return (
            jsonify({"msg:": f"failed to parse request for create_chat_session - {err.messages}", "trace": None}),
            400,
        )

    llm = data["llm"]
    db = data["db"]

    vector_store_type = VectorStoreType.TIDB
    embedding_model_type = EmbeddingModelType.SENTENCE_TRANSFORMER
    embedding_model_config = SentenceTransformerEmbeddingModelConfig()

    if db["type"] == DBType.MYSQL:
        db_config = MySQLConnConfig(
            host=db["config"]["host"],
            user=db["config"]["user"],
            password=db["config"].get("password", None),
            database=db["config"].get("database", None),
            port=db["config"]["port"],
        )
    else:
        e = ValueError(f"Unsupported db type: {db['type']}")
        return jsonify({"msg": str(e), "trace": None}), 400

    if llm["type"] == LLMType.GEMINI:
        llm_config = GeminiLLMClientConfig(
            api_key=llm["config"]["api_key"],
        )
    else:
        e = ValueError(f"Unsupported LLM type: {llm['type']}")
        return jsonify({"msg": str(e), "trace": None}), 400

    try:
        chat_session_id = str(uuid.uuid4())
        chat_handler = None

        if db["type"] == DBType.MYSQL:
            chat_handler = MySQLChatHandler(
                embedding_model_type=EmbeddingModelType(embedding_model_type),
                embedding_model_config=embedding_model_config,
                vector_store_type=VectorStoreType(vector_store_type),
                llm_type=LLMType(llm["type"]),
                llm_client_config=llm_config,
                db_conn_config=db_config,
                chat_session_id=chat_session_id,
            )
        CHAT_SESSION_CACHE[chat_session_id] = chat_handler
        return jsonify({"message": "Chat handler init successfully.", "chat_session_id": chat_session_id}), 200
    except Exception as e:
        error = {"msg": "failed to create chat handler", "trace": traceback.format_exc()}
        logger.error(error)
        return jsonify(error), 500


@chat.route("/send_message", methods=["POST"])
def send_message():
    schema = SendMessageSchema()
    try:
        data = schema.load(request.json)
        logger.info("Got request: {}".format(data))
    except ValidationError as err:
        error = {"msg": f"failed to parse request for send_message - {err.messages}", "trace": None}
        return jsonify(error), 400

    try:
        chat_handler: ChatHandler = CHAT_SESSION_CACHE.get(data["chat_session_id"], None)
        if not chat_handler:
            error = {"msg": "Chat handler not initialized for this client.", "trace": None}
            logger.error(error)
            return jsonify(error), 400
        chat_response: ChatResponse = chat_handler.answer_user_question(data["question"])
        result = {
            "sql": chat_response.sql,
            "message": chat_response.message,
            "natural_language_answer": chat_response.natural_language_answer,
            "data": chat_response.data,
        }
        return jsonify({"result": result}), 200
    except Exception as e:
        error = {"msg": "failed to send message", "trace": traceback.format_exc()}
        logger.error(error)
        return jsonify(error), 500

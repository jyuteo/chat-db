import uuid
import traceback

from flask import Blueprint, session, jsonify, request
from marshmallow import ValidationError

from embedding_models import EmbeddingModelType, SentenceTransformerEmbeddingModelConfig
from vector_store import VectorStoreType
from db_client import DBType, MySQLConnConfig
from llm import LLMType, GeminiLLMClientConfig
from chat_handler import ChatHandler, MySQLChatHandler
from api.request_schemas import CreateChatSessionSchema, SendMessageSchema

chat = Blueprint("chat", __name__, url_prefix="/chat")

CHAT_SESSION_CACHE = dict()


@chat.route("/create", methods=["POST"])
def create_chat_session():
    schema = CreateChatSessionSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error:": f"failed to parse request for create_chat_session - {err.messages}"}), 400

    llm = data["llm"]
    db = data["db"]

    vector_store_type = VectorStoreType.TIDB
    embedding_model_type = EmbeddingModelType.SENTENCE_TRANSFORMER
    embedding_model_config = SentenceTransformerEmbeddingModelConfig()

    if db["type"] == DBType.MYSQL:
        db_config = MySQLConnConfig(
            host=db["config"]["host"],
            user=db["config"]["user"],
            password=db["config"]["password"],
            database=db["config"]["database"],
        )
    else:
        e = ValueError(f"Unsupported db type: {db['type']}")
        return jsonify({"error": str(e)}), 400

    if llm["type"] == LLMType.GEMINI:
        llm_config = GeminiLLMClientConfig(
            api_key=llm["config"]["api_key"],
        )
    else:
        e = ValueError(f"Unsupported LLM type: {llm['type']}")
        return jsonify({"error": str(e)}), 400

    chat_session_id = session.get("chat_session_id", None)
    if not chat_session_id:
        chat_session_id = str(uuid.uuid4())
        session["chat_session_id"] = chat_session_id

    try:
        if db["type"] == DBType.MYSQL:
            chat_handler = MySQLChatHandler(
                embedding_model_type=EmbeddingModelType(embedding_model_type),
                embedding_model_config=embedding_model_config,
                vector_store_type=VectorStoreType(vector_store_type),
                llm_type=LLMType(llm["type"]),
                llm_client_config=llm_config,
                db_conn_config=db_config,
            )
            CHAT_SESSION_CACHE[chat_session_id] = chat_handler
        return jsonify({"message": "Chat handler init successfully."}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@chat.route("/send_message", methods=["POST"])
def send_message():
    schema = SendMessageSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error:": f"failed to parse request for send_message - {err.messages}"}), 400

    chat_session_id = session.get("chat_session_id", None)
    if not chat_session_id:
        return jsonify({"error": "No active chat session for this client."}), 400

    try:
        chat_handler: ChatHandler = CHAT_SESSION_CACHE.get(chat_session_id, None)
        if not chat_handler:
            return jsonify({"error": "Chat handler not initialized for this client."}), 400
        result = chat_handler.answer_user_question(data["question"])
        return jsonify({"result": result}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

import uuid
import traceback

from flask import Blueprint, session, jsonify, request

from embedding_models import EmbeddingModelType, SentenceTransformerEmbeddingModelConfig
from vector_store import VectorStoreType, TiDBVectorStoreConfig
from db_client import DBType, MySQLConnConfig
from llm import LLMType, GeminiLLMClientConfig
from chat_handler import ChatHandler, MySQLChatHandler

chat = Blueprint("chat", __name__, url_prefix="/chat")

CHAT_SESSION_CACHE = dict()


@chat.route("/create", methods=["POST"])
def create_chat_session():
    data = request.json

    vector_store_type = data.get("vector_store", {}).get("type")
    vector_store_config = data.get("vector_store", {}).get("config", {})
    llm_type = data.get("llm", {}).get("type")
    llm_config = data.get("llm", {}).get("config", {})
    db_type = data.get("db", {}).get("type")
    db_config = data.get("db", {}).get("config", {})

    embedding_model_type = EmbeddingModelType.SENTENCE_TRANSFORMER
    embedding_model_config = SentenceTransformerEmbeddingModelConfig()

    if db_type == DBType.MYSQL:
        db_config = (
            MySQLConnConfig(
                host=db_config.get("host"),
                user=db_config.get("user"),
                password=db_config.get("password"),
                database=db_config.get("database"),
            ),
        )
    else:
        e = ValueError(f"Unsupported db type: {db_type}")
        return jsonify({"error": str(e)}), 400

    if vector_store_type == VectorStoreType.TIDB:
        vector_store_config = TiDBVectorStoreConfig(
            db_connection_string=vector_store_config.get("db_connection_string"),
            db_type=db_type,
        )
    else:
        e = ValueError(f"Unsupported vector store type: {vector_store_type}")
        return jsonify({"error": str(e)}), 400

    if llm_type == LLMType.GEMINI:
        llm_config = GeminiLLMClientConfig(
            api_key=llm_config.get("api_key"),
        )
    else:
        e = ValueError(f"Unsupported LLM type: {llm_type}")
        return jsonify({"error": str(e)}), 400

    chat_session_id = session.get("chat_session_id")
    if not chat_session_id:
        chat_session_id = str(uuid.uuid4())
        session["chat_session_id"]["id"] = chat_session_id

    try:
        if db_type == DBType.MYSQL:
            chat_handler = MySQLChatHandler(
                vector_store_type=VectorStoreType(vector_store_type),
                vector_store_config=vector_store_config,
                llm_type=LLMType(llm_type),
                llm_client_config=llm_config,
                db_conn_config=db_config,
                embedding_model_type=EmbeddingModelType(embedding_model_type),
                embedding_model_config=embedding_model_config,
            )
            CHAT_SESSION_CACHE[chat_session_id] = chat_handler
            print(chat_handler)
        return jsonify({"message": "Chat handler init successfully."}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@chat.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    question = data.get("question")

    chat_session_id = session.get("chat_session_id")
    if not chat_session_id:
        return jsonify({"error": "No active chat session for this client."}), 400

    try:
        chat_handler: ChatHandler = CHAT_SESSION_CACHE.get(chat_session_id, None)
        if not chat_handler:
            return jsonify({"error": "Chat handler not initialized for this client."}), 400
        result = chat_handler.answer_user_question(question)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

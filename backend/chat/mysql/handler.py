from chat import ChatHandler

from db_client import DBType, MySQLDBClient
from embedding_models import EmbeddingModelType
from vector_store import VectorStoreType
from llm import LLMType


class MySQLChatHandler(ChatHandler):
    def __init__(
        self,
        vector_store_type: VectorStoreType,
        embedding_model_type: EmbeddingModelType,
        llm_type: LLMType,
        db_host: str,
        db_user: str,
        db_password: str,
        db_name: str,
        db_port: int = 3306,
    ):
        super().__init__(
            vector_store_type=vector_store_type,
            embedding_model_type=embedding_model_type,
            llm_type=llm_type,
            db_type=DBType.MYSQL,
        )

        self.db_client: MySQLDBClient = self.init_db_client(
            host=db_host, user=db_user, password=db_password, db_name=db_name, port=db_port
        )

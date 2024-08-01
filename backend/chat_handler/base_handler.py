import re

from abc import ABC, abstractmethod
from dataclasses import dataclass

from db_client import DBType, DBConnConfig, DBClientFactory, DBClient
from embedding_models import EmbeddingModelType, EmbeddingModelConfig, EmbeddingModelFactory, EmbeddingModel
from vector_store import VectorStoreType, VectorStoreConfig, VectorStoreHandlerFactory, VectorStoreHandler
from llm import LLMType, LLMClientFactory, LLMClientConfig, LLMClient
from logger import get_logger

logger = get_logger()


@dataclass
class ChatResponse:
    sql: str = None
    message: str = None
    natural_language_answer: str = None


class ChatHandler(ABC):
    def __init__(
        self,
        vector_store_type: VectorStoreType,
        embedding_model_type: EmbeddingModelType,
        llm_type: LLMType,
        db_type: DBType,
        chat_session_id: str = "",
    ):
        self.chat_session_id = chat_session_id

        try:
            self.vector_store_type = VectorStoreType(vector_store_type)
            self.vector_store: VectorStoreHandler = None
        except ValueError:
            raise ValueError(f"Invalid vector store type: {vector_store_type}")

        try:
            self.embedding_model_type = EmbeddingModelType(embedding_model_type)
            self.embedding_model: EmbeddingModel = None
        except ValueError:
            raise ValueError(f"Invalid embedding model type: {embedding_model_type}")

        try:
            self.llm_type = LLMType(llm_type)
            self.llm_client: LLMClient = None
        except ValueError:
            raise ValueError(f"Invalid llm type: {llm_type}")

        try:
            self.db_type = DBType(db_type)
            self.db_client: DBClient = None
        except ValueError:
            raise ValueError(f"Invalid db type: {db_type}")

    def log_info(self, message):
        log_data = {"chat_session_id": self.chat_session_id, "msg": message}
        logger.info(log_data)

    def log_error(self, message):
        log_data = {"chat_session_id": self.chat_session_id, "msg": message}
        logger.error(log_data)

    def log_debug(self, message):
        log_data = {"chat_session_id": self.chat_session_id, "msg": message}
        logger.debug(log_data)

    def log_warning(self, message):
        log_data = {"chat_session_id": self.chat_session_id, "msg": message}
        logger.warning(log_data)

    def init_vector_store(self, vector_store_config: VectorStoreConfig) -> VectorStoreHandler:
        return VectorStoreHandlerFactory.create(self.vector_store_type, vector_store_config)

    def init_embedding_model(self, embedding_model_config: EmbeddingModelConfig) -> EmbeddingModel:
        return EmbeddingModelFactory.create(self.embedding_model_type, embedding_model_config)

    def init_llm_client(self, llm_client_config: LLMClientConfig) -> LLMClient:
        return LLMClientFactory.create(self.llm_type, llm_client_config)

    def init_db_client(self, db_conn_config: DBConnConfig) -> DBClient:
        return DBClientFactory.create(self.db_type, db_conn_config)

    def submit_prompt(self, prompt: str) -> str:
        response = self.llm_client.send_message(prompt)
        return response

    def parse_sql_and_message_from_llm_response(self, response: str) -> ChatResponse:
        pattern = r"Response\(sql='(.*?)', message='(.*?)'\)"
        match = re.search(pattern, response)
        if match:
            sql = match.group(1)
            message = match.group(2)
            return ChatResponse(sql=sql, message=message)
        else:
            logger.error("failed to parse sql and message from LLM response: {response}")
            return ChatResponse()

    def get_sql_from_llm(self, question: str, *args, **kwargs) -> ChatResponse:
        prompt_to_get_sql = self.generate_prompt_to_get_sql(question)
        self.log_info(f"Generated prompt to get sql: {prompt_to_get_sql}")
        response = self.submit_prompt(prompt_to_get_sql)
        self.log_info(f"Got sql reponse from LLM before parsing: {response}")
        sql_response = self.parse_sql_and_message_from_llm_response(response)
        self.log_info(f"Got sql reponse from LLM after parsing: {sql_response}")
        return sql_response

    @abstractmethod
    def generate_prompt_to_get_sql(self, question: str, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def generate_prompt_to_get_natural_language_answer(self, question: str, sql: str, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def is_sql_read_only_statement(self, sql: str) -> bool:
        pass

    @abstractmethod
    def get_natural_language_answer_from_llm(self, question: str, sql: str, *args, **kwargs) -> str:
        """
        Execute the SQL to get the data, then send the question and data to LLM
        to generate natural language answer.
        """
        pass

    @abstractmethod
    def answer_user_question(self, question: str, *args, **kwargs) -> str:
        pass

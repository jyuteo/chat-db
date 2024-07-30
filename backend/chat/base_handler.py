from abc import ABC, abstractmethod

from db_client import DBType, DBClientFactory, DBClient
from embedding_models import EmbeddingModelType, EmbeddingModelFactory, EmbeddingModel
from vector_store import VectorStoreType, VectorStoreHandlerFactory, VectorStoreHandler
from llm import LLMType, LLMClientFactory, LLMClient, LLMResponse


class ChatHandler(ABC):
    def __init__(
        self,
        vector_store_type: VectorStoreType,
        embedding_model_type: EmbeddingModelType,
        llm_type: LLMType,
        db_type: DBType,
    ):
        try:
            self.vector_store_type = VectorStoreType(vector_store_type)
            self.vector_store = None
        except ValueError:
            raise ValueError(f"Invalid vector store type: {vector_store_type}")

        try:
            self.embedding_model_type = EmbeddingModelType(embedding_model_type)
            self.embedding_model = None
        except ValueError:
            raise ValueError(f"Invalid embedding model type: {embedding_model_type}")

        try:
            self.llm_type = LLMType(llm_type)
            self.llm_client = None
        except ValueError:
            raise ValueError(f"Invalid llm type: {llm_type}")

        try:
            self.db_type = DBType(db_type)
            self.db_client = None
        except ValueError:
            raise ValueError(f"Invalid db type: {db_type}")

    def init_vector_store(self, *args, **kwargs) -> VectorStoreHandler:
        return VectorStoreHandlerFactory.create(self.vector_store_type, *args, **kwargs)

    def init_embedding_model(self, *args, **kwargs) -> EmbeddingModel:
        return EmbeddingModelFactory.create(self.embedding_model_type, *args, **kwargs)

    def init_llm_client(self, *args, **kwargs) -> LLMClient:
        return LLMClientFactory.create(self.llm_type, *args, **kwargs)

    def init_db_client(self, db_type: DBType, *args, **kwargs) -> DBClient:
        return DBClientFactory.create(db_type, *args, **kwargs)

    @abstractmethod
    def generate_prompt_to_get_sql(self, question: str, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def generate_prompt_to_get_natural_language_answer(self, question: str, sql: str, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def submit_prompt(self, prompt: str) -> LLMResponse:
        pass

    @abstractmethod
    def get_sql_from_llm(self, question: str, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def validate_sql(self, sql: str) -> bool:
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

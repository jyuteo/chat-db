from abc import ABC, abstractmethod

from data_types import DBType
from embedding_models import EmbeddingModel
from vector_store import VectorStoreHandler
from llm import LLMClient, LLMResponse
from db_client import DBClient


class PromptHandler(ABC):
    def __init__(self, db_type: DBType):
        self.db_type = db_type

    @abstractmethod
    def init_vector_store(self, *args, **kwargs) -> VectorStoreHandler:
        pass

    @abstractmethod
    def init_embedding_model(self, *args, **kwargs) -> EmbeddingModel:
        pass

    @abstractmethod
    def init_llm_client(self, *args, **kwargs) -> LLMClient:
        pass

    @abstractmethod
    def init_db_client(self, *args, **kwargs) -> DBClient:
        pass

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

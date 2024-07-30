from chat_handler import ChatHandler
from db_client import DBType, MySQLDBClient, MySQLConnConfig
from embedding_models import EmbeddingModelType, EmbeddingModelConfig, EmbeddingModel
from vector_store import VectorStoreType, VectorStoreConfig, VectorStoreHandler
from llm import LLMType, LLMClient, LLMClientConfig
from chat_handler import Prompts


class MySQLChatHandler(ChatHandler):
    def __init__(
        self,
        embedding_model_type: EmbeddingModelType,
        embedding_model_config: EmbeddingModelConfig,
        vector_store_type: VectorStoreType,
        vector_store_config: VectorStoreConfig,
        llm_type: LLMType,
        llm_client_config: LLMClientConfig,
        db_conn_config: MySQLConnConfig,
    ):
        super().__init__(
            embedding_model_type=embedding_model_type,
            vector_store_type=vector_store_type,
            llm_type=llm_type,
            db_type=DBType.MYSQL,
        )

        self.embedding_model: EmbeddingModel = self.init_embedding_model(embedding_model_config=embedding_model_config)

        vector_store_config.embedding_model_name = self.embedding_model.model_name
        vector_store_config.embedding_model_dim = self.embedding_model.embedding_dim
        self.vector_store: VectorStoreHandler = self.init_vector_store(vector_store_config)

        self.llm_client: LLMClient = self.init_llm_client(llm_client_config)

        self.db_client: MySQLDBClient = self.init_db_client(db_conn_config)

    def generate_prompt_to_get_sql(self, question: str) -> str:
        """
        1. Generate embedding for question, and search for similar question-sql pairs from vector store
        2. Generate prompt to get sql from llm
        """
        prompt = Prompts.INITIAL_PROMPT.format(db_type=self.db_type)
        return prompt

    def generate_prompt_to_get_natural_language_answer(self, question: str, sql: str) -> str:
        pass

    def validate_sql(self, sql: str) -> bool:
        pass

    def is_sql_read_only_statement(self, sql: str) -> bool:
        pass

    def get_natural_language_answer_from_llm(self, question: str, sql: str, *args, **kwargs) -> str:
        """
        Execute the SQL to get the data, then send the question and data to LLM
        to generate natural language answer.
        """
        pass

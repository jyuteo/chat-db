from logger import get_logger

from chat_handler import ChatHandler
from db_client import DBType, MySQLDBClient, MySQLConnConfig
from embedding_models import EmbeddingModelType, EmbeddingModelConfig, EmbeddingModel
from vector_store import VectorStoreType, VectorStoreHandler, TiDBVectorStoreConfig
from llm import LLMType, LLMClient, LLMClientConfig
from chat_handler import Prompts

logger = get_logger()


class MySQLChatHandler(ChatHandler):
    def __init__(
        self,
        embedding_model_type: EmbeddingModelType,
        embedding_model_config: EmbeddingModelConfig,
        vector_store_type: VectorStoreType,
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

        if vector_store_type == VectorStoreType.TIDB:
            vector_store_config = TiDBVectorStoreConfig(
                db_type=DBType.MYSQL,
                embedding_model_name=self.embedding_model.model_name,
                embedding_model_dim=self.embedding_model.embedding_dim,
            )
        else:
            raise ValueError(f"Invalid vector store type: {vector_store_type}")
        self.vector_store: VectorStoreHandler = self.init_vector_store(vector_store_config)

        self.llm_client: LLMClient = self.init_llm_client(llm_client_config)

        self.db_client: MySQLDBClient = self.init_db_client(db_conn_config)

        self.table_schemas_in_db = dict()
        for table in self.db_client.get_tables_in_database():
            self.table_schemas_in_db[table] = self.db_client.get_table_schema(table)

    def generate_prompt_to_get_sql(self, question: str) -> str:
        """
        1. Generate embedding for question, and search for similar question-sql pairs from vector store
        2. Generate prompt to get sql from llm
        """
        question_embedding = self.embedding_model.get_embedding(question)
        similar_question_sql_pairs = self.vector_store.get_top_k_similar_question_sql_pairs_with_question_embedding(
            question_embedding
        )
        question_sql_pairs = []
        for pair, _ in similar_question_sql_pairs:
            question_sql_pairs.append(Prompts.QUESTION_SQL_PAIR.format(question=pair.question, sql=pair.sql))

        prompt = (
            Prompts.INITIAL_PROMPT.format(db_type=self.db_type)
            + "\n"
            + Prompts.GENERAL_QUESTION_SQL_PAIRS_WITHOUT_TABLE.format(question_sql_pairs="\n".join(question_sql_pairs))
            + "\n"
            + Prompts.TABLE_SCHEMA_IN_DB_PROMPT.format(table_schemas="\n".join(self.table_schemas_in_db.values()))
            + Prompts.USER_QUESTION_PROMPT.format(question=question)
        )
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

    def answer_user_question(self, question: str, *args, **kwargs) -> str:
        logger.info(f"Received user question: {question}")
        prompt = self.generate_prompt_to_get_sql(question)
        print(prompt)
        logger.info(f"Generated prompt to get sql: {prompt}")
        # response = self.submit_prompt(prompt)
        # logger.info(f"Response from LLM: {response}")
        # return response

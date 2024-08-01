from collections import defaultdict
from typing import List, Dict

import sqlparse
from chat_handler import ChatHandler, ChatResponse, PromptToGetNaturalLanguageAnswer, PromptToGetSQLAnswer
from db_client import DBType, MySQLConnConfig, MySQLDBClient
from embedding_models import EmbeddingModel, EmbeddingModelConfig, EmbeddingModelType
from llm import LLMClient, LLMClientConfig, LLMType
from logger import get_logger
from sqlparse.tokens import Token
from vector_store import TiDBVectorStoreConfig, VectorStoreHandler, VectorStoreType

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
        chat_session_id: str = "",
    ):
        super().__init__(
            embedding_model_type=embedding_model_type,
            vector_store_type=vector_store_type,
            llm_type=llm_type,
            db_type=DBType.MYSQL,
            chat_session_id=chat_session_id,
        )
        self.embedding_model: EmbeddingModel = self.init_embedding_model(embedding_model_config=embedding_model_config)

        if vector_store_type == VectorStoreType.TIDB:
            vector_store_config = TiDBVectorStoreConfig(
                db_type=DBType.MYSQL,
                embedding_model_type=embedding_model_type,
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

        self.similar_db_tables_from_knowledge_base = (
            self.get_similar_db_table_schemas_from_knowledge_base_with_table_schemas_in_db()
        )

    def get_similar_db_table_schemas_from_knowledge_base_with_table_schemas_in_db(self) -> Dict:
        similar_db_table_schemas = dict()
        for _, table_schema in self.table_schemas_in_db.items():
            table_schema_embedding = self.embedding_model.get_embedding(table_schema)
            similar_db_table_info = self.vector_store.get_top_k_similar_db_table_info_with_table_schema_embedding(
                table_schema_embedding, k=2
            )
            for db_table, _ in similar_db_table_info:
                similar_db_table_schemas[(db_table.database_name, db_table.table_name)] = db_table.table_schema
        return similar_db_table_schemas

    def generate_prompt_to_get_sql(self, question: str) -> str:
        """
        1. Generate embedding for question, and search for similar question-sql pairs from vector store
        2. Generate prompt to get sql from llm with similar question-sql pairs as knowledge base
        """
        question_embedding = self.embedding_model.get_embedding(question)
        similar_question_sql_pairs = self.vector_store.get_top_k_similar_question_sql_pairs_with_question_embedding(
            question_embedding, k=10, min_similarity=0.5
        )

        question_sql_pairs = defaultdict(list)
        table_schemas = defaultdict(list)
        for pair, _ in similar_question_sql_pairs:
            if pair.database_name and pair.table_name:
                question_sql_pairs[(pair.database_name, pair.table_name)].append(
                    PromptToGetSQLAnswer.QUESTION_SQL_PAIR.format(question=pair.question, sql=pair.sql)
                )
                table_schemas[(pair.database_name, pair.table_name)] = (
                    self.vector_store.get_db_table_info_by_database_name_and_table_name(
                        database_name=pair.database_name, table_name=pair.table_name
                    ).table_schema
                )
            else:
                question_sql_pairs["general"].append(
                    PromptToGetSQLAnswer.QUESTION_SQL_PAIR.format(question=pair.question, sql=pair.sql)
                )

        for (
            db_table,
            table_schema,
        ) in self.get_similar_db_table_schemas_from_knowledge_base_with_table_schemas_in_db().items():
            (db_name, table_name) = db_table
            if (db_name, table_name) not in table_schemas:
                table_schemas[(db_name, table_name)] = table_schema
                similar_question_sql_pairs = (
                    self.vector_store.get_top_k_similar_question_sql_pairs_with_question_embedding(
                        question_embedding,
                        k=5,
                        min_similarity=0.3,
                        filters={"database_name": db_name, "table_name": table_name},
                    )
                )
                for pair, _ in similar_question_sql_pairs:
                    question_sql_pairs[(pair.database_name, pair.table_name)].append(
                        PromptToGetSQLAnswer.QUESTION_SQL_PAIR.format(question=pair.question, sql=pair.sql)
                    )

        prompt = PromptToGetSQLAnswer.INITIAL_PROMPT.format(db_type=self.db_type)
        for k, pairs in question_sql_pairs.items():
            if k == "general":
                prompt += "\n" + PromptToGetSQLAnswer.GENERAL_QUESTION_SQL_PAIRS_WITHOUT_TABLE.format(
                    question_sql_pairs="\n".join(pairs)
                )
            else:
                prompt += "\n" + PromptToGetSQLAnswer.QUESTION_SQL_PAIRS_FOR_TABLE.format(
                    table_schema=table_schemas[k], question_sql_pairs="\n".join(pairs)
                )
        prompt += (
            "\n"
            + PromptToGetSQLAnswer.TABLE_SCHEMA_IN_DB_PROMPT.format(
                table_schemas="\n".join(self.table_schemas_in_db.values())
            )
            + PromptToGetSQLAnswer.USER_QUESTION_PROMPT.format(question=question)
        )
        return prompt

    def generate_prompt_to_get_natural_language_answer(self, question: str, data: List[str]) -> str:
        prompt = (
            PromptToGetNaturalLanguageAnswer.INITIAL_PROMPT.format(db_type=self.db_type)
            + "\n"
            + "\n".join(
                [PromptToGetNaturalLanguageAnswer.SQL_DATA_PAIR.format(sql=s, data=d) for s, d in data if d is not None]
            )
            + "\n"
            + PromptToGetNaturalLanguageAnswer.USER_QUESTION_PROMPT.format(question=question)
        )
        return prompt

    def is_sql_read_only_statement(self, sql: str) -> bool:
        write_keywords = {"INSERT", "UPDATE", "DELETE", "ALTER", "DROP", "CREATE"}
        parsed = sqlparse.parse(sql)

        for stmt in parsed:
            for token in stmt.tokens:
                if token.ttype in [Token.Keyword.DML, Token.Keyword.DDL]:
                    if token.value.upper() in write_keywords:
                        return False
        return True

    def get_natural_language_answer_from_llm(self, question: str, sql_response: ChatResponse) -> str:
        if not self.is_sql_read_only_statement(sql_response.sql):
            return None

        sqls = sqlparse.parse(sql_response.sql)
        data = [None] * len(sqls)
        for i, stmt in enumerate(sqls):
            try:
                result = self.db_client.execute_query(str(stmt))
                data[i] = result
            except Exception as e:
                self.log_error(f"failed to executed sql from LLM response: {str(stmt)}. error: {e}")

        if all(x is None for x in data):
            return None
        else:
            prompt = self.generate_prompt_to_get_natural_language_answer(question, zip(sqls, data))
            self.log_info(f"Generated prompt to get natural language answer: {prompt}")
            response = self.submit_prompt(prompt)
            self.log_info(f"Got natural language answer from LLM before parsing: {response}")
            natural_language_response = self.parse_sql_and_message_from_llm_response(response)
            self.log_info(f"Got natural language answer from LLM after parsing: {natural_language_response}")
            return natural_language_response.message

    def answer_user_question(self, question: str) -> str:
        self.log_info(f"Received question: {question}")
        sql_response = self.get_sql_from_llm(question)
        natural_language_answer = self.get_natural_language_answer_from_llm(question, sql_response)
        if natural_language_answer:
            sql_response.natural_language_answer = natural_language_answer
        return sql_response

import os
import dotenv
import redis

from flask import Flask
from flask_cors import CORS
from flask_session import Session

from app.api import db

dotenv.load_dotenv()


def init_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SECRET_KEY"] = os.getenv("FLASK_SESSION_SECRET_KEY")
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_KEY_PREFIX"] = "session:"
    app.config["SESSION_REDIS"] = redis.StrictRedis(host="localhost", port=6379, db=0)
    Session(app)

    app.register_blueprint(db)

    return app


def list_routes(app):
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods))
        print(f"{rule.endpoint:30s} {methods:20s} {rule}")


if __name__ == "__main__":
    app = init_app()
    list_routes(app)
    app.run(host="127.0.0.1", port=5000, debug=False)


# import os
# import dotenv

# from embedding_models import SentenceTransformerEmbeddingModel
# from vector_store import DBTableInfo, QuestionSQL
# from vector_store.tidb import TiDBVectorStoreHandler
# from data_types import DBType
# from db_client import MySQLDBClient

# dotenv.load_dotenv()

# # embedding_model = SentenceTransformerEmbeddingModel()

# # data = [
# #     ("dog", embedding_model.get_embedding("dog"), {"key3": "value"}),
# #     ("fish", embedding_model.get_embedding("fish"), {"key2": "value"}),
# #     ("tree", embedding_model.get_embedding("tree"), {"key1": "value"}),
# # ]

# # data = [
# #     DBTableInfo(
# #         database_name="database1",
# #         table_name="table1",
# #         table_schema="table_schema1",
# #         table_schema_embedding=embedding_model.get_embedding("table_schema1"),
# #     ),
# #     DBTableInfo(
# #         database_name="database2",
# #         table_name="table2",
# #         table_schema="table_schema2",
# #         table_schema_embedding=embedding_model.get_embedding("table_schema2"),
# #     ),
# #     DBTableInfo(
# #         database_name="database3",
# #         table_name="table3",
# #         table_schema="table_schema3",
# #         table_schema_embedding=embedding_model.get_embedding("table_schema3"),
# #     ),
# # ]

# # data = [
# #     QuestionSQL(
# #         database_name="database1",
# #         table_name="table1",
# #         question="question1",
# #         question_embedding=embedding_model.get_embedding("question1"),
# #         sql="sql1",
# #         metadatas={"key1": "value1"},
# #     ),
# #     QuestionSQL(
# #         # database_name="database2",
# #         # table_name="table2",
# #         question="question2",
# #         question_embedding=embedding_model.get_embedding("question2"),
# #         sql="sql2",
# #         metadatas={"key2": "value2"},
# #     ),
# #     QuestionSQL(
# #         database_name="database3",
# #         table_name="table3",
# #         question="question3",
# #         question_embedding=embedding_model.get_embedding("question3"),
# #         sql="sql3",
# #         metadatas={"key3": "value3"},
# #     ),
# # ]

# # handler = TiDBVectorStoreHandler(
# #     os.environ.get("TIDB_CONNECTION_STRING"),
# #     DBType.MYSQL,
# #     embedding_model.model_name,
# #     embedding_model.embedding_dim,
# #     reset_db=False,
# # )
# # print(
# #     handler.get_top_k_similar_question_sql_pairs_with_question_embedding(
# #         embedding_model.get_embedding("question2"), filters={"database_name": "database1"}
# #     )
# # )
# # handler.insert_question_sql_pairs(data)
# # handler.insert_db_table_info(data)
# # print(handler.get_db_table_info_by_database_name_and_table_name("database1", "table1"))


# # handler.insert_to_knowledge_base(data)
# # handler.retrieve_top_k_similar_items(embedding_model.get_embedding("swimming animal"))

# db_client = MySQLDBClient(host="localhost", user="root", password="12345678", database="test")

# print(db_client.execute_query("show processlist;"))
# print(db_client.execute_query("select * from orders;"))
# # for row in result:
# #     print(row)
# # db_client.close()

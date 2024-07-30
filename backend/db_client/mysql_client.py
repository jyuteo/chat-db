from dataclasses import dataclass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from db_client import DBClient, DBConnConfig
from logger import get_logger

logger = get_logger()


@dataclass
class MySQLConnConfig(DBConnConfig):
    host: str
    user: str
    password: str
    database: str
    port: int = 3306


class MySQLDBClient(DBClient):
    def __init__(self, db_conn_config: MySQLConnConfig):
        self.host = db_conn_config.host
        self.user = db_conn_config.user
        self.password = db_conn_config.password
        self.database = db_conn_config.database
        self.port = db_conn_config.port
        self.db_conn = self.connect()

    def connect(self) -> Engine:
        try:
            connection_url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            engine = create_engine(connection_url, pool_pre_ping=True)
            logger.info("Successfully connected to MySQL database")
            return engine
        except Exception as e:
            logger.error(f"Error connecting to MySQL platform: {e}")
            raise e

    def execute_query(self, query: str):
        try:
            with self.db_conn.connect() as connection:
                result = connection.execute(text(query))
                rows = result.fetchall()
                columns = result.keys()
                result.close()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise e

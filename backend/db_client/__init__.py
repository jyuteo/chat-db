from enum import Enum

from .base_client import DBClient, DBConnConfig
from .mysql_client import MySQLDBClient, MySQLConnConfig


class DBType(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


class DBClientFactory:
    @staticmethod
    def create(db_type: DBType, db_conn_config: DBConnConfig) -> DBClient:
        if isinstance(db_conn_config, MySQLConnConfig):
            assert db_type == DBType.MYSQL
            return MySQLDBClient(db_conn_config)
        else:
            raise ValueError(f"Unsupported db type: {db_conn_config.__class__.__name__}")

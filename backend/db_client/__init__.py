from enum import Enum

from .base_client import DBClient
from .mysql_client import MySQLDBClient


class DBType(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


class DBClientFactory:
    @staticmethod
    def create(db_type: DBType, *args, **kwargs) -> DBClient:
        if db_type == DBType.MYSQL:
            return MySQLDBClient(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported db type: {db_type}")

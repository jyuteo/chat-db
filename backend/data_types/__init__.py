from enum import Enum


class DBType(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"

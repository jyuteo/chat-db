from prompt import PromptHandler

from data_types import DBType


class MySQLPromptHandler(PromptHandler):
    def __init__(self, db_type: DBType):
        super().__init__(db_type)

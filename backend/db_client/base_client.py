from abc import ABC, abstractmethod


class DBClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def execute_query(self, query: str):
        pass

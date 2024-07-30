from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class DBConnConfig:
    pass


class DBClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def execute_query(self, query: str):
        pass

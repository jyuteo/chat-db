from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    sql: str = None


@dataclass
class LLMClientConfig:
    pass


class LLMClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def send_message(self, message: str) -> LLMResponse:
        pass

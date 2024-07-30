from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    sql: str = None


class LLMClient(ABC):
    def __init__(self, max_token: int = 14000):
        self.max_token = max_token

    @abstractmethod
    def send_message(self, message: str) -> LLMResponse:
        pass

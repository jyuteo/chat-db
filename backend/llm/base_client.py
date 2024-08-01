from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMClientConfig:
    pass


class LLMClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def send_message(self, message: str) -> str:
        pass

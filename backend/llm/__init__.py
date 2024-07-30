from enum import Enum

from .base_client import LLMClient, LLMResponse
from .openai_client import OpenAILLMClient


class LLMType(str, Enum):
    OPENAI = "openai"


class LLMClientFactory:
    @staticmethod
    def create(llm_type: LLMType, *args, **kwargs) -> LLMClient:
        if llm_type == LLMType.OPENAI:
            return OpenAILLMClient(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported llm type: {llm_type}")

from enum import Enum

from .base_client import LLMClient, LLMClientConfig
from .openai_client import OpenAILLMClient
from .gemini_client import GeminiLLMClient, GeminiLLMClientConfig


class LLMType(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


class LLMClientFactory:
    @staticmethod
    def create(llm_type: LLMType, llm_client_config: LLMClientConfig) -> LLMClient:
        if isinstance(llm_client_config, GeminiLLMClientConfig):
            assert llm_type == LLMType.GEMINI
            return GeminiLLMClient(llm_client_config)
        else:
            raise ValueError(f"Unsupported llm type: {llm_type}")

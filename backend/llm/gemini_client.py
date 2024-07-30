from dataclasses import dataclass
from enum import Enum

import google.generativeai as genai

from llm import LLMClient, LLMClientConfig


class GeminiModelName(str, Enum):
    GEMINI_15_FLASH = "gemini-1.5-flash"


@dataclass
class GeminiLLMClientConfig(LLMClientConfig):
    api_key: str
    gemini_model_name: str = GeminiModelName.GEMINI_15_FLASH
    temperature: float = 0.7


class GeminiLLMClient(LLMClient):
    def __init__(
        self,
        config: GeminiLLMClientConfig,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        genai.configure(api_key=config.api_key)
        self.gemini_model = genai.GenerativeModel(config.gemini_model_name)

        model_info = genai.get_model(f"models/{config.gemini_model_name}")
        self.input_token_limit, self.output_token_limit = model_info.input_token_limit, model_info.output_token_limit

        self.chat = self.gemini_model.start_chat(history=[])
        self.chat_history = list()

    def send_message(self, message: str) -> str:
        response = self.chat.send_message(message)
        self.chat_history.append({"user": message, "bot": response.text})
        return response.text

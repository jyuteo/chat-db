from enum import Enum
from typing import List

import backoff
import tiktoken
from openai import OpenAI, OpenAIError

from llm import LLMClient


class OpenAIModelName(str, Enum):
    GPT_35_TURBO_0125 = "gpt-3.5-turbo-0125"


class OpenAILLMClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        openai_model_name: OpenAIModelName = OpenAIModelName.GPT_35_TURBO_0125,
        max_token: int = 14000,
        max_response_token: int = 4096,
        temperature: float = 0.7,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.openai_client = OpenAI(api_key=api_key)

        self.openai_model = openai_model_name
        self.max_response_token = max_response_token
        self.temperature = temperature

    def send_message(self, message: str) -> str:
        processed_messages = self.process_message(message)
        responses = []

        for msg in processed_messages:
            response = self._send_to_openai(msg)
            responses.append(response)

        return " ".join(responses)

    def process_message(self, message: str) -> List[str]:
        tokenizer = tiktoken.encoding_for_model("gpt-4")
        tokens = tokenizer.encode(message)

        if len(tokens) <= self.max_token:
            return [message]

        chunks = []
        for i in range(0, len(tokens), self.max_token):
            chunk_tokens = tokens[i : i + self.max_token]
            chunks.append(tokenizer.decode(chunk_tokens))

        return chunks

    @backoff.on_exception(backoff.expo, OpenAIError)
    def _send_to_openai(self, message: str) -> str:
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=message,
                stop=None,
                temperature=self.temperature,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return str(e)

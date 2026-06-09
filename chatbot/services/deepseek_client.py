from dataclasses import dataclass
from typing import Optional

import httpx
from django.conf import settings

from chatbot.constants import MAX_HISTORY_MESSAGES, MAX_HISTORY_TOTAL_CHARS
from chatbot.prompts import get_system_prompt


class DeepSeekAPIError(Exception):
    """Raised when DeepSeek API returns an error response."""


@dataclass(frozen=True)
class DeepSeekResponse:
    content: str
    model: str


class DeepSeekClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = (base_url or settings.DEEPSEEK_BASE_URL).rstrip("/")
        self.model = model or settings.DEEPSEEK_MODEL
        self.timeout = timeout or settings.DEEPSEEK_TIMEOUT

    def _trim_history(self, history: list[dict[str, str]]) -> list[dict[str, str]]:
        trimmed = list(history)

        while len(trimmed) > MAX_HISTORY_MESSAGES:
            trimmed.pop(0)

        while trimmed and sum(len(message["content"]) for message in trimmed) > MAX_HISTORY_TOTAL_CHARS:
            trimmed.pop(0)

        return trimmed

    def _build_messages(self, question: str, history: list[dict[str, str]]) -> list[dict[str, str]]:
        messages = [{"role": "system", "content": get_system_prompt()}]
        for message in self._trim_history(history):
            messages.append({"role": message["role"], "content": message["content"]})
        messages.append({"role": "user", "content": question})
        return messages

    def ask(self, question: str, history: Optional[list[dict[str, str]]] = None) -> DeepSeekResponse:
        if not self.api_key:
            raise DeepSeekAPIError("DEEPSEEK_API_KEY is not configured.")

        payload = {
            "model": self.model,
            "messages": self._build_messages(question, history or []),
            "stream": False,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            raise DeepSeekAPIError(
                f"DeepSeek API request failed: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise DeepSeekAPIError(f"DeepSeek API connection error: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
            model = data.get("model", self.model)
        except (KeyError, IndexError, TypeError) as exc:
            raise DeepSeekAPIError("Unexpected DeepSeek API response format.") from exc

        return DeepSeekResponse(content=content.strip(), model=model)

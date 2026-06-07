from dataclasses import dataclass
from typing import Optional

import httpx
from django.conf import settings

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

    def ask(self, question: str) -> DeepSeekResponse:
        if not self.api_key:
            raise DeepSeekAPIError("DEEPSEEK_API_KEY is not configured.")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": question},
            ],
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

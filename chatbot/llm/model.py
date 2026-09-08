from functools import lru_cache

from django.conf import settings
from langchain_openai import ChatOpenAI


@lru_cache
def get_chat_model() -> ChatOpenAI:
    """Return one reusable, OpenAI-compatible DeepSeek chat model per worker."""
    return ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        timeout=settings.DEEPSEEK_TIMEOUT,
        max_retries=2,
    )

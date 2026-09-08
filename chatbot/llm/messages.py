from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, trim_messages
from langchain_core.messages.utils import count_tokens_approximately

from chatbot.constants import MAX_HISTORY_MESSAGES, MAX_HISTORY_TOKENS


def to_messages(history: list[dict[str, str]]) -> list[BaseMessage]:
    """Convert validated request history into provider-independent LangChain messages."""
    return [
        HumanMessage(content=message["content"])
        if message["role"] == "user"
        else AIMessage(content=message["content"])
        for message in history
    ]


def trim_history(history: list[dict[str, str]]) -> list[BaseMessage]:
    """Keep the latest valid conversation context within a bounded token budget."""
    recent_history = to_messages(history[-MAX_HISTORY_MESSAGES:])
    return trim_messages(
        recent_history,
        max_tokens=MAX_HISTORY_TOKENS,
        token_counter=count_tokens_approximately,
        strategy="last",
        start_on="human",
        allow_partial=False,
    )

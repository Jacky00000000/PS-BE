from functools import lru_cache

from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from openai import APIConnectionError, APIStatusError, APITimeoutError

from chatbot.llm.exceptions import ChatModelError
from chatbot.llm.model import get_chat_model
from chatbot.llm.prompts import get_system_prompt


@lru_cache
def get_chat_chain():
    """Build the synchronous conversation chain used by the HTTP API."""
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=get_system_prompt()),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    return prompt | get_chat_model() | StrOutputParser()


def invoke_chat(question: str, history) -> str:
    """Invoke the chain and map provider failures to an application exception."""
    try:
        return get_chat_chain().invoke({"question": question, "history": history})
    except (APIConnectionError, APIStatusError, APITimeoutError) as exc:
        raise ChatModelError("The AI service is temporarily unavailable.") from exc

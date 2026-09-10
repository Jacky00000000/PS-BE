from functools import lru_cache
from dataclasses import dataclass
import json
import logging

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from openai import APIConnectionError, APIStatusError, APITimeoutError

from chatbot.constants import MAX_TOOL_CALLS_PER_RESPONSE
from chatbot.llm.exceptions import ChatModelError
from chatbot.llm.model import get_chat_model
from chatbot.llm.prompts import (
    FINAL_ANSWER_INSTRUCTION,
    TOOL_INSTRUCTIONS,
    get_system_prompt,
)
from chatbot.tools.registry import get_tool_map, get_tools

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentResult:
    answer: str
    sources: list[dict[str, str]]


@lru_cache
def get_agent_model():
    """Bind the explicit allow-list of application tools to the chat model."""
    return get_chat_model().bind_tools(get_tools())


def _content_as_text(content) -> str:
    if isinstance(content, str):
        return content

    return str(content)


def _attach_source_ids(
    tool_name: str,
    result: str,
    sources: list[dict[str, str]],
) -> tuple[str, list[dict[str, str]]]:
    if tool_name != "web_search":
        return result, []

    try:
        search_data = json.loads(result)
    except (TypeError, ValueError):
        return result, []

    source_by_url = {}
    for source in sources:
        source_by_url[source["url"]] = source
    new_sources = []
    for item in search_data.get("results", []):
        url = item.get("url")
        if not url:
            continue

        source = source_by_url.get(url)
        if source is None:
            source = {
                "id": f"S{len(sources) + len(new_sources) + 1}",
                "title": item.get("title", "Untitled"),
                "url": url,
            }
            source_by_url[url] = source
            new_sources.append(source)
        item["source_id"] = source["id"]

    return json.dumps(search_data, ensure_ascii=False), new_sources


def invoke_agent(question: str, history: list[BaseMessage]) -> AgentResult:
    """Run one bounded tool call batch and return the model's final answer."""
    messages: list[BaseMessage] = [
        SystemMessage(content=f"{get_system_prompt()}\n{TOOL_INSTRUCTIONS}"),
        *history,
        HumanMessage(content=question),
    ]
    model = get_agent_model()
    tools = get_tool_map()
    sources: list[dict[str, str]] = []
    try:
        response = model.invoke(messages)
    except (APIConnectionError, APIStatusError, APITimeoutError) as exc:
        logger.exception(
            "LLM request failed: stage=tool_call error_type=%s status_code=%s",
            type(exc).__name__,
            getattr(exc, "status_code", None),
        )
        raise ChatModelError("The AI service is temporarily unavailable.") from exc

    if not response.tool_calls:
        answer = _content_as_text(response.content).strip()
        return AgentResult(answer=answer, sources=sources)

    tool_calls = response.tool_calls[:MAX_TOOL_CALLS_PER_RESPONSE]
    if len(response.tool_calls) > MAX_TOOL_CALLS_PER_RESPONSE:
        logger.warning(
            "Ignoring %s tool calls beyond the per-response limit",
            len(response.tool_calls) - MAX_TOOL_CALLS_PER_RESPONSE,
        )

    messages.append(response.model_copy(update={"tool_calls": tool_calls}))

    try:
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool = tools.get(tool_name)
            if tool is None:
                logger.warning("Agent requested unregistered tool: %s", tool_name)
                result = f"Tool '{tool_name}' is not available."
            else:
                try:
                    logger.info("Agent invoking tool: %s", tool_name)
                    result = tool.invoke(tool_call["args"])
                except Exception:
                    logger.exception("Agent tool failed: %s", tool_name)
                    result = f"Tool '{tool_name}' failed. Continue without it."

            result_text, new_sources = _attach_source_ids(
                tool_name,
                _content_as_text(result),
                sources,
            )
            sources.extend(new_sources)

            messages.append(
                ToolMessage(
                    content=result_text,
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                )
            )
    except (APIConnectionError, APIStatusError, APITimeoutError) as exc:
        logger.exception(
            "LLM request failed: stage=tool_call error_type=%s status_code=%s",
            type(exc).__name__,
            getattr(exc, "status_code", None),
        )
        raise ChatModelError("The AI service is temporarily unavailable.") from exc

    final_instruction = HumanMessage(content=FINAL_ANSWER_INSTRUCTION)
    final_messages = [*messages, final_instruction]

    try:
        final_response = get_chat_model().invoke(final_messages)
    except (APIConnectionError, APIStatusError, APITimeoutError) as exc:
        logger.exception(
            "LLM request failed: stage=final_answer error_type=%s status_code=%s",
            type(exc).__name__,
            getattr(exc, "status_code", None),
        )
        raise ChatModelError("The AI service is temporarily unavailable.") from exc

    answer = _content_as_text(final_response.content).strip()
    return AgentResult(answer=answer, sources=sources)

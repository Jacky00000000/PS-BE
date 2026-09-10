import json
import logging

import httpx
from django.conf import settings
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def web_search(query: str) -> str:
    """Search the public web for current facts, news, prices, schedules, or events.

    Use this tool whenever the answer may have changed since the model's knowledge
    cutoff. Do not use it for information that is already provided in the chat.
    """
    if not settings.TAVILY_API_KEY:
        logger.error("web_search unavailable: TAVILY_API_KEY is not configured")
        return "Web search is unavailable because TAVILY_API_KEY is not configured."

    try:
        response = httpx.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {settings.TAVILY_API_KEY}"},
            json={
                "query": query[:500],
                "search_depth": "advanced",
                "max_results": 3,
                "include_answer": True,
            },
            timeout=settings.TAVILY_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "web_search provider error: status=%s body=%s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        return "Web search is temporarily unavailable. Tell the user that you could not verify current information."
    except httpx.TimeoutException:
        logger.error("web_search timed out after %s seconds", settings.TAVILY_TIMEOUT)
        return "Web search timed out. Tell the user that you could not verify current information."
    except httpx.HTTPError:
        logger.exception("web_search connection error")
        return "Web search is temporarily unavailable. Tell the user that you could not verify current information."
    except ValueError:
        logger.exception("web_search returned invalid JSON")
        return "Web search is temporarily unavailable. Tell the user that you could not verify current information."

    results = [
        {
            "title": item.get("title", "Untitled"),
            "url": item.get("url", ""),
            "content": item.get("content", "")[:2000],
        }
        for item in data.get("results", [])
    ]
    logger.info(
        "web_search succeeded: result_count=%s request_id=%s",
        len(results),
        data.get("request_id", "unknown"),
    )
    if not results and not data.get("answer"):
        logger.warning(
            "web_search completed without results: request_id=%s",
            data.get("request_id", "unknown"),
        )
        return (
            "Web search completed successfully but returned no results. "
            "Do not say that the search API is broken; tell the user that no current result was found."
        )

    return json.dumps({"results": results}, ensure_ascii=False)

import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def trace(event: str, **payload) -> None:
    """Write opt-in, JSON-formatted agent execution details to the server log."""
    if not settings.CHATBOT_AGENT_TRACE_ENABLED:
        return

    logger.info(
        "agent_trace(websearch)=%s",
        json.dumps({"event": event, **payload}, ensure_ascii=False, default=str),
    )

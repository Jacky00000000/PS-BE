from typing import Optional
from dataclasses import dataclass

from chatbot.llm.agent import AgentResult, invoke_agent
from chatbot.llm.messages import trim_history
from chatbot.models import ChatbotRecord


@dataclass(frozen=True)
class ChatResponse:
    record: ChatbotRecord
    sources: list[dict[str, str]]


class ChatService:
    def __init__(self, invoke=invoke_agent) -> None:
        self._invoke = invoke

    def ask(
        self,
        question: str,
        history: Optional[list[dict[str, str]]] = None,
    ) -> ChatResponse:
        agent_result: AgentResult = self._invoke(
            question,
            trim_history(history or []),
        )

        record = ChatbotRecord.objects.create(
            question=question,
            answer=agent_result.answer,
        )
        return ChatResponse(record=record, sources=agent_result.sources)

    def list_records(self) -> list[ChatbotRecord]:
        return list(ChatbotRecord.objects.all())

    def get_record(self, record_id) -> ChatbotRecord:
        return ChatbotRecord.objects.get(id=record_id)

    def delete_record(self, record_id) -> None:
        record = self.get_record(record_id)
        record.delete()

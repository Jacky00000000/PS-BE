from typing import Optional

from chatbot.llm.chains import invoke_chat
from chatbot.llm.messages import trim_history
from chatbot.models import ChatbotRecord


class ChatService:
    def __init__(self, invoke=invoke_chat) -> None:
        self._invoke = invoke

    def ask(
        self,
        question: str,
        history: Optional[list[dict[str, str]]] = None,
    ) -> ChatbotRecord:
        answer = self._invoke(
            question,
            trim_history(history or []),
        )

        return ChatbotRecord.objects.create(
            question=question,
            answer=answer.strip(),
        )

    def list_records(self) -> list[ChatbotRecord]:
        return list(ChatbotRecord.objects.all())

    def get_record(self, record_id) -> ChatbotRecord:
        return ChatbotRecord.objects.get(id=record_id)

    def delete_record(self, record_id) -> None:
        record = self.get_record(record_id)
        record.delete()

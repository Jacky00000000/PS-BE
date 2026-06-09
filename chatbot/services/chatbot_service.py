from typing import Optional

from chatbot.models import ChatbotRecord
from chatbot.services.deepseek_client import DeepSeekClient


class ChatbotService:
    def __init__(self, client: Optional[DeepSeekClient] = None) -> None:
        self._client = client or DeepSeekClient()

    def ask_question(
        self,
        question: str,
        history: Optional[list[dict[str, str]]] = None,
    ) -> ChatbotRecord:
        cleaned_question = question.strip()
        if not cleaned_question:
            raise ValueError("Question cannot be empty.")

        response = self._client.ask(cleaned_question, history=history or [])

        return ChatbotRecord.objects.create(
            question=cleaned_question,
            answer=response.content,
        )

    def list_records(self) -> list[ChatbotRecord]:
        return list(ChatbotRecord.objects.all())

    def get_record(self, record_id) -> ChatbotRecord:
        return ChatbotRecord.objects.get(id=record_id)

    def delete_record(self, record_id) -> None:
        record = self.get_record(record_id)
        record.delete()

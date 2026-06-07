import uuid

from django.db import models


class ChatbotRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chatbot_record"
        ordering = ["-created_at"]
        verbose_name = "Chatbot Record"
        verbose_name_plural = "Chatbot Records"

    def __str__(self) -> str:
        preview = self.question[:50]
        suffix = "..." if len(self.question) > 50 else ""
        return f"{preview}{suffix}"

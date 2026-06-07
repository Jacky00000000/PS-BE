from django.contrib import admin

from chatbot.models import ChatbotRecord


@admin.register(ChatbotRecord)
class ChatbotRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "question_preview", "created_at")
    search_fields = ("question", "answer")
    readonly_fields = ("id", "question", "answer", "created_at")
    ordering = ("-created_at",)

    @admin.display(description="Question")
    def question_preview(self, obj: ChatbotRecord) -> str:
        return str(obj)

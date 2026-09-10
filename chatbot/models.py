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
        verbose_name = "Chatbot Record" #後台顯示名稱
        verbose_name_plural = "Chatbot Records" 

    #截取问题的前 50 个字符。如果问题超过 50 字则加上省略号，否则不加。返回简短预览文本，让管理员在后台能一眼看出这条记录问了什么。
    def __str__(self) -> str:
        preview = self.question[:50]
        if len(self.question) > 50:
            suffix = "..."
        else:
            suffix = ""

        return f"{preview}{suffix}"

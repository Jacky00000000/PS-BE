from rest_framework import serializers

from chatbot.constants import MAX_MESSAGE_CONTENT_LENGTH
from chatbot.models import ChatbotRecord


class HistoryMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField(
        max_length=MAX_MESSAGE_CONTENT_LENGTH,
        trim_whitespace=True,
        min_length=1,
    )


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=MAX_MESSAGE_CONTENT_LENGTH, trim_whitespace=True)
    history = HistoryMessageSerializer(many=True, required=False)


class ChatbotRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotRecord
        fields = ["id", "question", "answer", "created_at"]
        read_only_fields = fields

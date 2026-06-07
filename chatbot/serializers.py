from rest_framework import serializers

from chatbot.models import ChatbotRecord


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=4000, trim_whitespace=True)


class ChatbotRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotRecord
        fields = ["id", "question", "answer", "created_at"]
        read_only_fields = fields

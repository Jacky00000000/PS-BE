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

    def validate_history(self, history: list[dict[str, str]]) -> list[dict[str, str]]:
        expected_role = "user"
        for message in history:
            if message["role"] != expected_role:
                raise serializers.ValidationError(
                    "History must start with a user message and alternate between user and assistant."
                )
            if expected_role == "user":
                expected_role = "assistant"
            else:
                expected_role = "user"
        return history

#Make class object to json
class ChatbotRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotRecord
        fields = ["id", "question", "answer", "created_at"]
        read_only_fields = fields

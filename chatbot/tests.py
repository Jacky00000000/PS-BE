from django.test import TestCase
from rest_framework.exceptions import ValidationError

from chatbot.constants import MAX_HISTORY_MESSAGES, MAX_HISTORY_TOTAL_CHARS
from chatbot.serializers import AskQuestionSerializer
from chatbot.services.deepseek_client import DeepSeekClient


class AskQuestionSerializerTests(TestCase):
    def test_accepts_question_without_history(self):
        serializer = AskQuestionSerializer(data={"question": "你是谁？"})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["question"], "你是谁？")
        self.assertNotIn("history", serializer.validated_data)

    def test_accepts_question_with_history(self):
        serializer = AskQuestionSerializer(
            data={
                "question": "你几多岁？",
                "history": [
                    {"role": "user", "content": "你叫咩名？"},
                    {"role": "assistant", "content": "我係楊公鵬。"},
                ],
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data["history"]), 2)

    def test_rejects_invalid_history_role(self):
        serializer = AskQuestionSerializer(
            data={
                "question": "test",
                "history": [{"role": "system", "content": "nope"}],
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("history", serializer.errors)

    def test_rejects_empty_history_content(self):
        serializer = AskQuestionSerializer(
            data={
                "question": "test",
                "history": [{"role": "user", "content": "   "}],
            }
        )
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class DeepSeekClientHistoryTests(TestCase):
    def setUp(self):
        self.client = DeepSeekClient(api_key="test-key")

    def test_build_messages_includes_system_history_and_question(self):
        messages = self.client._build_messages(
            "你几多岁？",
            [
                {"role": "user", "content": "你叫咩名？"},
                {"role": "assistant", "content": "我係楊公鵬。"},
            ],
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["content"], "你叫咩名？")
        self.assertEqual(messages[2]["content"], "我係楊公鵬。")
        self.assertEqual(messages[-1], {"role": "user", "content": "你几多岁？"})

    def test_trim_history_removes_oldest_when_message_count_exceeded(self):
        history = [
            {"role": "user", "content": f"message-{index}"}
            for index in range(MAX_HISTORY_MESSAGES + 5)
        ]

        trimmed = self.client._trim_history(history)

        self.assertEqual(len(trimmed), MAX_HISTORY_MESSAGES)
        self.assertEqual(trimmed[0]["content"], "message-5")

    def test_trim_history_removes_oldest_when_total_chars_exceeded(self):
        chunk = "a" * 1000
        history = [{"role": "user", "content": chunk} for _ in range(20)]

        trimmed = self.client._trim_history(history)

        total_chars = sum(len(message["content"]) for message in trimmed)
        self.assertLessEqual(total_chars, MAX_HISTORY_TOTAL_CHARS)

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from chatbot.api.serializers import AskQuestionSerializer
from chatbot.application.chat_service import ChatService
from chatbot.constants import MAX_HISTORY_MESSAGES
from chatbot.llm.messages import trim_history


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


    def test_rejects_history_that_does_not_start_with_user(self):
        serializer = AskQuestionSerializer(
            data={"question": "test", "history": [{"role": "assistant", "content": "nope"}]}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("history", serializer.errors)


class ChatHistoryTests(TestCase):
    def test_trim_history_removes_oldest_when_message_count_exceeded(self):
        history = [
            {"role": "user", "content": f"message-{index}"}
            for index in range(MAX_HISTORY_MESSAGES + 5)
        ]

        trimmed = trim_history(history)

        self.assertEqual(len(trimmed), MAX_HISTORY_MESSAGES)
        self.assertEqual(trimmed[0].content, "message-5")

    def test_trim_history_preserves_message_roles(self):
        trimmed = trim_history(
            [
                {"role": "user", "content": "你叫咩名？"},
                {"role": "assistant", "content": "我係楊公鵬。"},
            ]
        )

        self.assertEqual(trimmed[0].type, "human")
        self.assertEqual(trimmed[1].type, "ai")


class ChatServiceTests(TestCase):
    def test_ask_sends_only_request_history_to_the_chain(self):
        captured = {}

        def fake_invoke(question, history):
            captured["question"] = question
            captured["history"] = history
            return "測試答案"

        record = ChatService(invoke=fake_invoke).ask(
            question="你好嗎？",
            history=[{"role": "user", "content": "之前問題"}],
        )

        self.assertEqual(record.answer, "測試答案")
        self.assertEqual(captured["question"], "你好嗎？")
        self.assertEqual(captured["history"][0].content, "之前問題")

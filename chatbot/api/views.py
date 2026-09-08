from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from chatbot.api.serializers import AskQuestionSerializer, ChatbotRecordSerializer
from chatbot.application.chat_service import ChatService
from chatbot.llm.exceptions import ChatModelError


class AskQuestionView(APIView):
    service_class = ChatService

    def post(self, request: Request) -> Response:
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = self.service_class()
        try:
            record = service.ask(
                question=serializer.validated_data["question"],
                history=serializer.validated_data.get("history") or [],
            )
        except ChatModelError:
            return Response(
                {"detail": "The AI service is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            ChatbotRecordSerializer(record).data,
            status=status.HTTP_201_CREATED,
        )

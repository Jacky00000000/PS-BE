from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from chatbot.models import ChatbotRecord
from chatbot.serializers import AskQuestionSerializer, ChatbotRecordSerializer
from chatbot.services.chatbot_service import ChatbotService
from chatbot.services.deepseek_client import DeepSeekAPIError


class AskQuestionView(APIView):
    def post(self, request: Request) -> Response:
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ChatbotService()
        try:
            record = service.ask_question(serializer.validated_data["question"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except DeepSeekAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(
            ChatbotRecordSerializer(record).data,
            status=status.HTTP_201_CREATED,
        )


class ChatbotRecordListView(APIView):
    def get(self, request: Request) -> Response:
        records = ChatbotRecord.objects.all()
        serializer = ChatbotRecordSerializer(records, many=True)
        return Response(serializer.data)


class ChatbotRecordDetailView(APIView):
    def get(self, request: Request, record_id) -> Response:
        record = get_object_or_404(ChatbotRecord, id=record_id)
        return Response(ChatbotRecordSerializer(record).data)

    def delete(self, request: Request, record_id) -> Response:
        record = get_object_or_404(ChatbotRecord, id=record_id)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

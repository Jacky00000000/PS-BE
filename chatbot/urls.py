from django.urls import path

from chatbot.views import AskQuestionView, ChatbotRecordDetailView, ChatbotRecordListView

urlpatterns = [
    path("ask/", AskQuestionView.as_view(), name="chatbot-ask"),
    path("records/", ChatbotRecordListView.as_view(), name="chatbot-record-list"),
    path(
        "records/<uuid:record_id>/",
        ChatbotRecordDetailView.as_view(),
        name="chatbot-record-detail",
    ),
]

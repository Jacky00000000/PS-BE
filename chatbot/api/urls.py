from django.urls import path

from chatbot.api.views import AskQuestionView

urlpatterns = [
    path("ask/", AskQuestionView.as_view(), name="chatbot-ask"),
]

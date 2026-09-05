from django.urls import path

from conversations import views

app_name = "conversations"

urlpatterns = [
    path("dashboard/conversations/", views.conversation_list, name="list"),
]

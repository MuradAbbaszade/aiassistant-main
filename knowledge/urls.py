from django.urls import path

from knowledge import views

app_name = "knowledge"

urlpatterns = [
    path("dashboard/knowledge/", views.knowledge_list, name="list"),
    path("dashboard/knowledge/create/", views.knowledge_create, name="create"),
    path("dashboard/knowledge/<int:pk>/update/", views.knowledge_update, name="update"),
    path("dashboard/knowledge/<int:pk>/delete/", views.knowledge_delete, name="delete"),
]

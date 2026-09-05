from django.urls import path

from ai import views

app_name = "ai"

urlpatterns = [
    path("dashboard/ai-settings/", views.ai_settings_view, name="settings"),
]

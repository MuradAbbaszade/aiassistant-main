from django.urls import path

from marketing import views

app_name = "marketing"

urlpatterns = [
    path("", views.landing, name="landing"),
]

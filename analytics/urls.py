from django.urls import path

from analytics import views

app_name = "analytics"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/analytics/", views.analytics_page, name="analytics"),
]

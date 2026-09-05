from django.urls import path

from leads import views

app_name = "leads"

urlpatterns = [
    path("dashboard/leads/", views.lead_list, name="list"),
    path("dashboard/leads/<int:pk>/status/", views.lead_update_status, name="update_status"),
]

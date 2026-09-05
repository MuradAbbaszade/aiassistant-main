from django.urls import path

from channels import views, webhooks

app_name = "channels"

urlpatterns = [
    path("dashboard/channels/", views.channel_list, name="list"),
    path("dashboard/channels/instagram/connect/", views.instagram_connect, name="instagram_connect"),
    path("dashboard/channels/instagram/disconnect/", views.instagram_disconnect, name="instagram_disconnect"),
    path("dashboard/channels/instagram/test-send/", views.instagram_test_send, name="instagram_test_send"),
    path("dashboard/channels/instagram/resubscribe/", views.instagram_resubscribe, name="instagram_resubscribe"),
    path("dashboard/channels/instagram/simulate/", views.instagram_simulate_webhook, name="instagram_simulate"),
    path("webhooks/instagram/", webhooks.instagram_webhook, name="instagram_webhook"),
]

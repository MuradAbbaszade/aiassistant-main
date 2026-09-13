from django.contrib import admin

from integrations.models import WebhookDelivery, WebhookEndpoint


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("id", "business", "name", "url", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "url", "business__id", "business__name")
    readonly_fields = ("secret", "created_at", "updated_at")


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "endpoint", "event_type", "status", "attempts", "response_code", "created_at")
    list_filter = ("status", "event_type")
    search_fields = ("endpoint__business__id", "event_type")
    readonly_fields = ("payload", "response_body", "created_at", "updated_at")

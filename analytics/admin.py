from django.contrib import admin

from analytics.models import AnalyticsSnapshot


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ("business", "date", "messages_today", "ai_answered", "new_leads", "response_rate")
    list_filter = ("business",)

from django.contrib import admin

from ai.models import AISettings


@admin.register(AISettings)
class AISettingsAdmin(admin.ModelAdmin):
    list_display = ("business", "assistant_name", "language", "tone", "business_type")

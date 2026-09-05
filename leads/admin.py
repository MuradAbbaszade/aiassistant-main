from django.contrib import admin

from leads.models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "contact", "status", "source", "created_at")
    list_filter = ("status", "source", "business")
    search_fields = ("name", "contact", "intent")

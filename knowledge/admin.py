from django.contrib import admin

from knowledge.models import KnowledgeItem


@admin.register(KnowledgeItem)
class KnowledgeItemAdmin(admin.ModelAdmin):
    list_display = ("title", "business", "type", "updated_at")
    list_filter = ("type", "business")
    search_fields = ("title", "content")

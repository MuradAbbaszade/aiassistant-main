from django.contrib import admin

from businesses.models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "plan", "city", "phone", "created_at")
    list_filter = ("type", "plan", "city")
    search_fields = ("id", "name", "city")
    list_editable = ("plan",)

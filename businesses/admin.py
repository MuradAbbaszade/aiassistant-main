from django.contrib import admin

from businesses.models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "city", "phone", "created_at")
    list_filter = ("type", "city")
    search_fields = ("id", "name", "city")

from django.contrib import admin

from channels.models import Channel


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("business", "type", "status", "handle")
    list_filter = ("type", "status")

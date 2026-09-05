from django.contrib import admin

from conversations.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "business", "channel", "status", "lead_potential", "updated_at")
    list_filter = ("channel", "status", "business")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "label", "timestamp")
    list_filter = ("sender", "label")

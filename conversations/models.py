from django.db import models

from businesses.models import Business


class ConversationStatus(models.TextChoices):
    AI = "ai", "AI"
    HUMAN = "human", "İnsan"
    CLOSED = "closed", "Bağlı"


class ChannelChoice(models.TextChoices):
    INSTAGRAM = "instagram", "Instagram"
    WHATSAPP = "whatsapp", "WhatsApp"
    WEBSITE = "website", "Vebsayt"


class Conversation(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="conversations")
    customer_name = models.CharField(max_length=120)
    external_user_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Instagram IGSID or other channel user id",
    )
    channel = models.CharField(max_length=32, choices=ChannelChoice.choices, default=ChannelChoice.INSTAGRAM)
    status = models.CharField(max_length=16, choices=ConversationStatus.choices, default=ConversationStatus.AI)
    lead_potential = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.customer_name} ({self.channel})"


class MessageSender(models.TextChoices):
    CUSTOMER = "customer", "Müştəri"
    AI = "ai", "AI"
    HUMAN = "human", "İnsan"


class MessageLabel(models.TextChoices):
    AI_ANSWERED = "ai_answered", "AI cavab verdi"
    HUMAN_REQUIRED = "human_required", "İnsan lazımdır"
    LEAD = "lead", "Lead"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=16, choices=MessageSender.choices)
    content = models.TextField()
    label = models.CharField(max_length=32, choices=MessageLabel.choices, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return f"{self.sender}: {self.content[:40]}"

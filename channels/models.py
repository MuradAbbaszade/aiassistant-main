from django.db import models

from businesses.models import Business


class ChannelType(models.TextChoices):
    INSTAGRAM = "instagram", "Instagram"
    WHATSAPP = "whatsapp", "WhatsApp"
    WEBSITE = "website", "Vebsayt"


class ChannelStatus(models.TextChoices):
    CONNECTED = "connected", "Qoşulub"
    DISCONNECTED = "disconnected", "Qoşulmayıb"
    COMING_SOON = "coming_soon", "Tezliklə"
    LIVE = "live", "Canlı (Meta API)"


class Channel(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="channels")
    type = models.CharField(max_length=32, choices=ChannelType.choices)
    status = models.CharField(
        max_length=32, choices=ChannelStatus.choices, default=ChannelStatus.DISCONNECTED
    )
    handle = models.CharField(max_length=120, blank=True)
    external_id = models.CharField(max_length=120, blank=True, help_text="Instagram professional account ID")
    access_token = models.TextField(blank=True, help_text="OAuth access token for this channel")
    token_expires_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("business", "type")]
        ordering = ["type"]

    def __str__(self) -> str:
        return f"{self.business_id}:{self.type}"

    @property
    def is_live(self) -> bool:
        return self.status == ChannelStatus.LIVE and bool(self.access_token and self.external_id)

from django.db import models

from businesses.models import Business
from conversations.models import Conversation


class LeadStatus(models.TextChoices):
    NEW = "New", "Yeni"
    CONTACTED = "Contacted", "Əlaqə saxlanılıb"
    QUALIFIED = "Qualified", "Uyğundur"
    CONVERTED = "Converted", "Müştəri oldu"
    LOST = "Lost", "İtirilib"


class LeadSource(models.TextChoices):
    INSTAGRAM = "instagram", "Instagram"
    WHATSAPP = "whatsapp", "WhatsApp"
    WEBSITE = "website", "Vebsayt"
    DEMO = "demo", "Demo"


class Lead(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="leads")
    name = models.CharField(max_length=120)
    contact = models.CharField(max_length=80)
    intent = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=32, choices=LeadSource.choices, default=LeadSource.DEMO)
    status = models.CharField(max_length=32, choices=LeadStatus.choices, default=LeadStatus.NEW)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.status}"

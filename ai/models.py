from django.db import models

from businesses.models import Business, BusinessType


class AISettings(models.Model):
    class Language(models.TextChoices):
        AZ = "az", "Azərbaycan"
        EN = "en", "English"
        RU = "ru", "Русский"

    class Tone(models.TextChoices):
        FRIENDLY = "friendly", "Dostyana"
        PROFESSIONAL = "professional", "Peşəkar"
        FORMAL = "formal", "Rəsmi"
        CASUAL = "casual", "Sərbəst"

    class ResponseLength(models.TextChoices):
        SHORT = "short", "Qısa"
        MEDIUM = "medium", "Orta"
        LONG = "long", "Ətraflı"

    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="ai_settings")
    assistant_name = models.CharField(max_length=100, default="AI Assistant")
    language = models.CharField(max_length=8, choices=Language.choices, default=Language.AZ)
    tone = models.CharField(max_length=32, choices=Tone.choices, default=Tone.FRIENDLY)
    response_length = models.CharField(
        max_length=16, choices=ResponseLength.choices, default=ResponseLength.MEDIUM
    )
    business_type = models.CharField(
        max_length=32, choices=BusinessType.choices, default=BusinessType.OTHER
    )
    rules = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.business_id and not self.business_type:
            self.business_type = self.business.type
        elif self.business_id:
            self.business_type = self.business.type
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"AISettings({self.business_id})"

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from businesses.models import Business


class UserProfile(models.Model):
    class OnboardingPath(models.TextChoices):
        NONE = "", "—"
        MANUAL = "manual", "Manual setup"
        MESSAGE = "message", "Message us"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=32, blank=True)
    email_verified = models.BooleanField(default=False)
    onboarding_path = models.CharField(
        max_length=16, choices=OnboardingPath.choices, blank=True, default=""
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owner_profiles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.email or self.user.username

    @property
    def full_name(self) -> str:
        return self.user.get_full_name() or self.user.email


class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_otps")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.code}"

    @property
    def is_valid(self) -> bool:
        return (not self.used) and timezone.now() < self.expires_at


def default_whatsapp_url() -> str:
    number = getattr(settings, "SUPPORT_WHATSAPP", "994705550117")
    digits = "".join(ch for ch in str(number) if ch.isdigit())
    return f"https://wa.me/{digits}"

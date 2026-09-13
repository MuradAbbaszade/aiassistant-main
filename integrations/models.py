from __future__ import annotations

import secrets

from django.db import models

from businesses.models import Business


class WebhookEvent(models.TextChoices):
    LEAD_CREATED = "lead.created", "lead.created"
    LEAD_UPDATED = "lead.updated", "lead.updated"


DEFAULT_WEBHOOK_EVENTS = [
    WebhookEvent.LEAD_CREATED,
    WebhookEvent.LEAD_UPDATED,
]


def generate_webhook_secret() -> str:
    return secrets.token_urlsafe(32)


class WebhookEndpoint(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="webhook_endpoints")
    name = models.CharField(max_length=120, default="CRM webhook")
    url = models.URLField(max_length=500)
    secret = models.CharField(max_length=64, default=generate_webhook_secret)
    is_active = models.BooleanField(default=True)
    events = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.business_id}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.events:
            self.events = list(DEFAULT_WEBHOOK_EVENTS)
        if not self.secret:
            self.secret = generate_webhook_secret()
        super().save(*args, **kwargs)

    def listens_for(self, event_type: str) -> bool:
        return event_type in (self.events or [])


class DeliveryStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


class WebhookDelivery(models.Model):
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="deliveries")
    event_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    status = models.CharField(
        max_length=16, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING, db_index=True
    )
    response_code = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "webhook deliveries"

    def __str__(self) -> str:
        return f"{self.event_type} → {self.endpoint_id} ({self.status})"

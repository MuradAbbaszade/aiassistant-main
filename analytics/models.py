from django.db import models

from businesses.models import Business


class AnalyticsSnapshot(models.Model):
    """Daily or point-in-time metrics per business. Charts can also be computed live."""

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="analytics_snapshots")
    date = models.DateField()
    messages_today = models.PositiveIntegerField(default=0)
    ai_answered = models.PositiveIntegerField(default=0)
    human_takeover = models.PositiveIntegerField(default=0)
    new_leads = models.PositiveIntegerField(default=0)
    response_rate = models.FloatField(default=0.0)
    messages_per_day = models.JSONField(default=list, blank=True)
    ai_vs_human = models.JSONField(default=dict, blank=True)
    lead_funnel = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("business", "date")]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.business_id} @ {self.date}"

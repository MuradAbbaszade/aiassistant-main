from django.db import models

from businesses.models import Business


class KnowledgeType(models.TextChoices):
    BUSINESS = "business", "Biznes"
    SERVICE = "service", "Xidmət"
    FAQ = "faq", "FAQ"
    POLICY = "policy", "Siyasət"
    DOCUMENT = "document", "Sənəd"


class KnowledgeItem(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="knowledge_items")
    type = models.CharField(max_length=32, choices=KnowledgeType.choices, default=KnowledgeType.FAQ)
    title = models.CharField(max_length=255)
    content = models.TextField()
    keywords = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.business_id}: {self.title}"

from django.db import models


class BusinessType(models.TextChoices):
    CONSTRUCTION = "construction", "Tikinti"
    MEDICAL = "medical", "Tibbi"
    RESTAURANT = "restaurant", "Restoran"
    REAL_ESTATE = "real_estate", "Daşınmaz əmlak"
    BEAUTY = "beauty", "Gözəllik"
    LEGAL = "legal", "Hüquq"
    EDUCATION = "education", "Təhsil"
    OTHER = "other", "Digər"


class Business(models.Model):
    id = models.SlugField(primary_key=True, max_length=64)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=32, choices=BusinessType.choices, default=BusinessType.OTHER)
    description = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    working_hours = models.CharField(max_length=200, blank=True)
    service_areas = models.JSONField(default=list, blank=True)
    speciality = models.JSONField(default=list, blank=True)
    cuisine = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "businesses"

    def __str__(self) -> str:
        return self.name

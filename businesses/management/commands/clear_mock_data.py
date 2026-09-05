"""Delete seeded mock tenants — production uses Instagram OAuth tenants only."""
from django.core.management.base import BaseCommand

from ai.models import AISettings
from analytics.models import AnalyticsSnapshot
from businesses.models import Business
from channels.models import Channel
from conversations.models import Conversation, Message
from knowledge.models import KnowledgeItem
from leads.models import Lead

MOCK_IDS = {
    "abc-construction",
    "dr-aysel-clinic",
    "urban-table",
    "prime-estate",
}


class Command(BaseCommand):
    help = "Remove mock seed businesses and related data"

    def handle(self, *args, **options):
        qs = Business.objects.filter(pk__in=MOCK_IDS)
        count = qs.count()
        # Cascades for most FKs; explicit for clarity
        AnalyticsSnapshot.objects.filter(business_id__in=MOCK_IDS).delete()
        Lead.objects.filter(business_id__in=MOCK_IDS).delete()
        Message.objects.filter(conversation__business_id__in=MOCK_IDS).delete()
        Conversation.objects.filter(business_id__in=MOCK_IDS).delete()
        Channel.objects.filter(business_id__in=MOCK_IDS).delete()
        KnowledgeItem.objects.filter(business_id__in=MOCK_IDS).delete()
        AISettings.objects.filter(business_id__in=MOCK_IDS).delete()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Removed {count} mock businesses."))

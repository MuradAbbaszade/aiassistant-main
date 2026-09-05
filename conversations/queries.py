from django.db.models import Q, QuerySet

from conversations.models import Conversation


def customer_conversations(business) -> QuerySet[Conversation]:
    """Real customer threads only — hide demo / simulated chats from the inbox."""
    qs = Conversation.objects.filter(business=business)
    return (
        qs.exclude(customer_name__iexact="Demo Müştəri")
        .exclude(customer_name__iexact="Demo Customer")
        .exclude(external_user_id__startswith="SIMULATED")
        .exclude(Q(external_user_id="") & Q(customer_name__icontains="demo"))
    )

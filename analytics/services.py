"""Live analytics computed from conversations, messages, and leads."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from conversations.models import Conversation, ConversationStatus, Message, MessageSender
from leads.models import Lead, LeadStatus


def compute_business_analytics(business, lang: str | None = None) -> dict[str, Any]:
    """Return KPI + chart payloads for a business (no AnalyticsSnapshot required)."""
    from core.i18n import get_translator

    tr = get_translator(lang)
    if not business:
        return _empty(tr)

    today = timezone.localdate()
    start_day = today - timedelta(days=6)
    msgs = Message.objects.filter(conversation__business=business)
    msgs_today = msgs.filter(timestamp__date=today)
    customer_today = msgs_today.filter(sender=MessageSender.CUSTOMER).count()
    ai_today = msgs_today.filter(sender=MessageSender.AI).count()
    human_today = msgs_today.filter(sender=MessageSender.HUMAN).count()
    answered_today = ai_today + human_today
    if customer_today:
        response_rate = min(1.0, answered_today / customer_today)
    else:
        customer_all = msgs.filter(sender=MessageSender.CUSTOMER).count()
        answered_all = msgs.filter(sender__in=[MessageSender.AI, MessageSender.HUMAN]).count()
        response_rate = min(1.0, answered_all / customer_all) if customer_all else 0.0

    new_leads_today = Lead.objects.filter(business=business, created_at__date=today).count()
    leads_total = Lead.objects.filter(business=business).count()

    ai_all = msgs.filter(sender=MessageSender.AI).count()
    human_all = msgs.filter(sender=MessageSender.HUMAN).count()
    human_takeovers = Conversation.objects.filter(
        business=business, status=ConversationStatus.HUMAN
    ).count()

    per_day_raw = (
        msgs.filter(timestamp__date__gte=start_day)
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(c=Count("id"))
    )
    per_day: dict[str, int] = {}
    for row in per_day_raw:
        day = row["day"]
        if day is None:
            continue
        key = day.date().isoformat() if hasattr(day, "date") else str(day)[:10]
        per_day[key] = int(row["c"])

    messages_per_day = []
    for i in range(7):
        d = start_day + timedelta(days=i)
        messages_per_day.append({"date": d.isoformat(), "count": per_day.get(d.isoformat(), 0)})

    funnel_counts = {
        row["status"]: row["c"]
        for row in Lead.objects.filter(business=business).values("status").annotate(c=Count("id"))
    }
    funnel_labels = {
        LeadStatus.NEW: tr["an.funnel.New"],
        LeadStatus.CONTACTED: tr["an.funnel.Contacted"],
        LeadStatus.QUALIFIED: tr["an.funnel.Qualified"],
        LeadStatus.CONVERTED: tr["an.funnel.Converted"],
        LeadStatus.LOST: tr["an.funnel.Lost"],
    }
    lead_funnel = {
        funnel_labels.get(status, status): int(funnel_counts.get(status, 0))
        for status, _label in LeadStatus.choices
    }

    return {
        "messages_today": msgs_today.count(),
        "ai_answered": ai_all,
        "human_takeover": human_takeovers or human_all,
        "new_leads": leads_total,
        "leads_today": new_leads_today,
        "response_rate": response_rate,
        "messages_per_day": messages_per_day,
        "ai_vs_human": {"ai": ai_all, "human": human_all},
        "lead_funnel": lead_funnel,
        "has_data": bool(msgs.exists() or leads_total),
    }


def _empty(tr=None) -> dict[str, Any]:
    from core.i18n import get_translator

    tr = tr or get_translator("az")
    today = timezone.localdate()
    start_day = today - timedelta(days=6)
    return {
        "messages_today": 0,
        "ai_answered": 0,
        "human_takeover": 0,
        "new_leads": 0,
        "response_rate": 0.0,
        "messages_per_day": [
            {"date": (start_day + timedelta(days=i)).isoformat(), "count": 0} for i in range(7)
        ],
        "ai_vs_human": {"ai": 0, "human": 0},
        "lead_funnel": {
            tr["an.funnel.New"]: 0,
            tr["an.funnel.Contacted"]: 0,
            tr["an.funnel.Qualified"]: 0,
            tr["an.funnel.Converted"]: 0,
            tr["an.funnel.Lost"]: 0,
        },
        "has_data": False,
    }

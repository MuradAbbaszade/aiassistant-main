import json

from django.shortcuts import render

from analytics.models import AnalyticsSnapshot
from conversations.models import Conversation
from core.decorators import demo_login_required
from knowledge.models import KnowledgeItem
from leads.models import Lead


@demo_login_required
def dashboard(request):
    business = request.current_business
    if not business:
        return render(request, "dashboard/empty.html")

    snap = AnalyticsSnapshot.objects.filter(business=business).order_by("-date").first()
    conversations = Conversation.objects.filter(business=business)[:6]
    leads = Lead.objects.filter(business=business)[:5]
    knowledge_count = KnowledgeItem.objects.filter(business=business).count()

    kpis = {
        "messages_today": snap.messages_today if snap else 0,
        "ai_answered": snap.ai_answered if snap else 0,
        "human_takeover": snap.human_takeover if snap else 0,
        "new_leads": snap.new_leads if snap else Lead.objects.filter(business=business).count(),
        "response_rate": int((snap.response_rate if snap else 0) * 100),
        "knowledge_count": knowledge_count,
    }
    return render(
        request,
        "dashboard/home.html",
        {
            "kpis": kpis,
            "conversations": conversations,
            "leads": leads,
            "active_nav": "dashboard",
        },
    )


@demo_login_required
def analytics_page(request):
    business = request.current_business
    snap = AnalyticsSnapshot.objects.filter(business=business).order_by("-date").first()
    funnel = snap.lead_funnel if snap else {}
    series = snap.messages_per_day if snap else []
    ai_vs = snap.ai_vs_human if snap else {"ai": 0, "human": 0}
    return render(
        request,
        "dashboard/analytics.html",
        {
            "snap": snap,
            "funnel_json": json.dumps(funnel),
            "series_json": json.dumps(series),
            "ai_vs_json": json.dumps(ai_vs),
            "response_rate_pct": int((snap.response_rate if snap else 0) * 100),
            "active_nav": "analytics",
        },
    )

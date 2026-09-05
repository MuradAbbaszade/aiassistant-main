import json

from django.shortcuts import render

from analytics.services import compute_business_analytics
from conversations.models import Conversation
from core.decorators import demo_login_required
from knowledge.models import KnowledgeItem
from leads.models import Lead


@demo_login_required
def dashboard(request):
    business = request.current_business
    if not business:
        return render(request, "dashboard/empty.html")

    stats = compute_business_analytics(business, getattr(request, "ui_lang", None))
    conversations = Conversation.objects.filter(business=business)[:6]
    leads = Lead.objects.filter(business=business)[:5]
    knowledge_count = KnowledgeItem.objects.filter(business=business).count()

    kpis = {
        "messages_today": stats["messages_today"],
        "ai_answered": stats["ai_answered"],
        "human_takeover": stats["human_takeover"],
        "new_leads": stats["new_leads"],
        "response_rate": int(stats["response_rate"] * 100),
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
    if not business:
        return render(request, "dashboard/empty.html")

    stats = compute_business_analytics(business, getattr(request, "ui_lang", None))
    return render(
        request,
        "dashboard/analytics.html",
        {
            "stats": stats,
            "funnel_json": json.dumps(stats["lead_funnel"]),
            "series_json": json.dumps(stats["messages_per_day"]),
            "ai_vs_json": json.dumps(stats["ai_vs_human"]),
            "response_rate_pct": int(stats["response_rate"] * 100),
            "active_nav": "analytics",
        },
    )

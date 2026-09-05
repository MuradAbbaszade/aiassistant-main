"""JSON API endpoints for demo chat, knowledge, leads, channels, analytics, business switch."""
from __future__ import annotations

import random
import time

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ai.services.responder import get_responder
from businesses.models import Business
from channels.models import Channel, ChannelStatus, ChannelType
from conversations.models import Conversation, Message, MessageLabel, MessageSender
from knowledge.models import KnowledgeItem
from knowledge.services.search import search_knowledge
from leads.models import Lead, LeadSource, LeadStatus


def _require_business(request, business_id: str | None = None) -> Business:
    bid = business_id or request.session.get("current_business_id") or settings.DEFAULT_BUSINESS_ID
    return get_object_or_404(Business, pk=bid)


@api_view(["POST"])
@permission_classes([AllowAny])
def switch_business(request):
    business_id = request.data.get("business_id")
    business = get_object_or_404(Business, pk=business_id)
    request.session["current_business_id"] = business.id
    request.session.pop("demo_conversation_id", None)
    return Response({"ok": True, "business_id": business.id, "name": business.name})


@api_view(["POST"])
@permission_classes([AllowAny])
def demo_chat(request):
    """
    POST /api/demo/chat/
    {business_id, message, history?, force_abc_scenario?}
    """
    message = (request.data.get("message") or "").strip()
    if not message:
        return Response({"error": "message required"}, status=status.HTTP_400_BAD_REQUEST)

    force_abc = bool(request.data.get("force_abc_scenario"))
    business_id = "abc-construction" if force_abc else request.data.get("business_id")
    business = _require_business(request, business_id)

    # Keep session in sync
    request.session["current_business_id"] = business.id

    history = request.data.get("history") or []
    if not isinstance(history, list):
        history = []

    # Realistic delay
    time.sleep(random.uniform(0.5, 0.8))

    conv_id = request.session.get("demo_conversation_id")
    conversation = None
    if conv_id:
        conversation = Conversation.objects.filter(pk=conv_id, business=business).first()
    if conversation is None:
        conversation = Conversation.objects.create(
            business=business,
            customer_name="Demo Customer",
            external_user_id="SIMULATED_DEMO_CHAT",
            channel="instagram",
            status="ai",
        )
        request.session["demo_conversation_id"] = conversation.id

    Message.objects.create(
        conversation=conversation,
        sender=MessageSender.CUSTOMER,
        content=message,
    )

    responder = get_responder()
    result = responder.respond(
        business=business,
        message=message,
        history=[str(h) for h in history],
        conversation=conversation,
        source=LeadSource.DEMO,
    )

    if not getattr(result, "should_reply", True) or not (result.answer or "").strip():
        payload = result.to_dict()
        payload["business_id"] = business.id
        payload["conversation_id"] = conversation.id
        payload["toast"] = None
        payload["skipped_reply"] = True
        return Response(payload)

    label = MessageLabel.AI_ANSWERED
    if result.requires_human:
        label = MessageLabel.HUMAN_REQUIRED
        conversation.status = "human"
    if result.lead_created:
        label = MessageLabel.LEAD
        conversation.lead_potential = True
    elif result.lead_potential:
        conversation.lead_potential = True
    conversation.save()

    Message.objects.create(
        conversation=conversation,
        sender=MessageSender.AI,
        content=result.answer,
        label=label,
    )

    payload = result.to_dict()
    payload["business_id"] = business.id
    payload["conversation_id"] = conversation.id
    payload["toast"] = None
    if result.lead_created:
        payload["toast"] = "🔥 Yeni potensial müştəri qeydə alındı!"
    return Response(payload)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def knowledge_api(request):
    business = _require_business(request, request.query_params.get("business_id") or request.data.get("business_id"))
    if request.method == "GET":
        items = KnowledgeItem.objects.filter(business=business)
        q = request.query_params.get("q")
        if q:
            scored = search_knowledge(business.id, q, limit=20)
            data = [
                {
                    "id": s.item.id,
                    "title": s.item.title,
                    "type": s.item.type,
                    "content": s.item.content,
                    "keywords": s.item.keywords,
                    "score": s.score,
                }
                for s in scored
            ]
        else:
            data = [
                {
                    "id": i.id,
                    "title": i.title,
                    "type": i.type,
                    "content": i.content,
                    "keywords": i.keywords,
                }
                for i in items
            ]
        return Response(data)

    keywords = request.data.get("keywords") or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    item = KnowledgeItem.objects.create(
        business=business,
        type=request.data.get("type") or "faq",
        title=request.data.get("title") or "Başlıqsız",
        content=request.data.get("content") or "",
        keywords=keywords,
    )
    return Response(
        {"id": item.id, "title": item.title, "type": item.type, "content": item.content},
        status=status.HTTP_201_CREATED,
    )


@api_view(["PATCH", "DELETE"])
@permission_classes([AllowAny])
def knowledge_detail_api(request, pk: int):
    business = _require_business(request)
    item = get_object_or_404(KnowledgeItem, pk=pk, business=business)
    if request.method == "DELETE":
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    for field in ("title", "content", "type"):
        if field in request.data:
            setattr(item, field, request.data[field])
    if "keywords" in request.data:
        kw = request.data["keywords"]
        if isinstance(kw, str):
            kw = [k.strip() for k in kw.split(",") if k.strip()]
        item.keywords = kw
    item.save()
    return Response(
        {
            "id": item.id,
            "title": item.title,
            "type": item.type,
            "content": item.content,
            "keywords": item.keywords,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def conversations_api(request):
    business = _require_business(request, request.query_params.get("business_id"))
    convs = Conversation.objects.filter(business=business).prefetch_related("messages")[:50]
    data = []
    for c in convs:
        data.append(
            {
                "id": c.id,
                "customer_name": c.customer_name,
                "channel": c.channel,
                "status": c.status,
                "lead_potential": c.lead_potential,
                "updated_at": c.updated_at.isoformat(),
                "messages": [
                    {
                        "id": m.id,
                        "sender": m.sender,
                        "content": m.content,
                        "label": m.label,
                        "timestamp": m.timestamp.isoformat(),
                    }
                    for m in c.messages.all()
                ],
            }
        )
    return Response(data)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def lead_status_api(request, pk: int):
    business = _require_business(request)
    lead = get_object_or_404(Lead, pk=pk, business=business)
    new_status = request.data.get("status")
    if new_status not in {c.value for c in LeadStatus}:
        return Response({"error": "invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    lead.status = new_status
    lead.save(update_fields=["status", "updated_at"])
    return Response({"id": lead.id, "status": lead.status})


@api_view(["POST"])
@permission_classes([AllowAny])
def instagram_connect_api(request):
    business = _require_business(request, request.data.get("business_id"))
    channel, _ = Channel.objects.get_or_create(
        business=business,
        type=ChannelType.INSTAGRAM,
        defaults={"status": ChannelStatus.DISCONNECTED},
    )
    channel.status = ChannelStatus.CONNECTED
    channel.handle = request.data.get("handle") or channel.handle or f"@{business.id}"
    channel.save()
    return Response(
        {"ok": True, "type": channel.type, "status": channel.status, "handle": channel.handle}
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def analytics_api(request):
    from analytics.services import compute_business_analytics

    business = _require_business(request, request.query_params.get("business_id"))
    stats = compute_business_analytics(business)
    return Response(
        {
            "messages_today": stats["messages_today"],
            "ai_answered": stats["ai_answered"],
            "human_takeover": stats["human_takeover"],
            "new_leads": stats["new_leads"],
            "response_rate": stats["response_rate"],
            "messages_per_day": stats["messages_per_day"],
            "ai_vs_human": stats["ai_vs_human"],
            "lead_funnel": stats["lead_funnel"],
        }
    )


# --- Future stubs (not wired for v1) ---
# POST /api/ai/chat/  → OpenAI provider
# POST /webhooks/whatsapp/
# POST /webhooks/instagram/

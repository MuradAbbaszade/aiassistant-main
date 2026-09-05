"""
Process Instagram Messaging webhooks → AI reply → send DM back (multi-tenant).
"""
from __future__ import annotations

import logging
from typing import Any

from django.db import transaction

from ai.services.responder import get_responder
from businesses.models import Business
from channels.models import Channel, ChannelStatus, ChannelType
from channels.services.instagram import (
    fetch_ig_username,
    get_credentials_for_ig_account,
    send_instagram_text,
)
from conversations.models import Conversation, Message, MessageLabel, MessageSender
from leads.models import LeadSource

logger = logging.getLogger(__name__)

SIMULATED_SENDER_PREFIX = "SIMULATED_"


def _is_simulated(sender_igsid: str) -> bool:
    return str(sender_igsid).startswith(SIMULATED_SENDER_PREFIX) or not str(sender_igsid).isdigit()


def _resolve_business(ig_account_id: str) -> Business | None:
    channel = (
        Channel.objects.filter(type=ChannelType.INSTAGRAM, external_id=str(ig_account_id))
        .select_related("business")
        .first()
    )
    return channel.business if channel else None


def _get_or_create_conversation(business: Business, sender_igsid: str, creds) -> Conversation:
    conv = (
        Conversation.objects.filter(
            business=business,
            channel="instagram",
            external_user_id=sender_igsid,
        )
        .order_by("-updated_at")
        .first()
    )
    if conv:
        return conv
    if _is_simulated(sender_igsid):
        display = "Simulyasiya müştəri"
    else:
        username = fetch_ig_username(sender_igsid, credentials=creds)
        display = f"@{username}" if username else f"IG:{sender_igsid[-6:]}"
    return Conversation.objects.create(
        business=business,
        customer_name=display,
        external_user_id=sender_igsid,
        channel="instagram",
        status="ai",
    )


def handle_instagram_webhook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    if payload.get("object") not in ("instagram", "page"):
        return {"handled": 0, "note": "ignored object", "object": payload.get("object")}

    for entry in payload.get("entry") or []:
        ig_id = str(entry.get("id") or "")
        for event in entry.get("messaging") or []:
            try:
                result = _handle_messaging_event(ig_id, event)
                if result:
                    results.append(result)
            except Exception as exc:
                logger.exception("Failed handling Instagram event: %s", exc)
                results.append({"ok": False, "error": str(exc)})

    return {"handled": len(results), "results": results}


def _maybe_send(*, sender_igsid: str, text: str, credentials) -> dict[str, Any]:
    """Send DM unless this is a local simulation sender."""
    if _is_simulated(sender_igsid):
        return {"skipped": True, "reason": "simulation_sender"}
    try:
        data = send_instagram_text(recipient_igsid=sender_igsid, text=text, credentials=credentials)
        return {"skipped": False, "api": data}
    except Exception as exc:
        logger.exception("Instagram send failed")
        return {"skipped": False, "error": str(exc)}


def _handle_messaging_event(ig_account_id: str, event: dict[str, Any]) -> dict[str, Any] | None:
    message = event.get("message") or {}
    if not message:
        return None
    if message.get("is_echo") or message.get("is_deleted"):
        return None

    sender_igsid = (event.get("sender") or {}).get("id")
    if not sender_igsid:
        return None

    creds = get_credentials_for_ig_account(ig_account_id)
    business = _resolve_business(ig_account_id)
    if not business or not creds:
        logger.error("No connected business/token for IG id %s", ig_account_id)
        return {"ok": False, "error": "business or token not found"}

    text = (message.get("text") or "").strip()
    if not text:
        reply = (
            "Mesajınızı aldım. Zəhmət olmasa sualınızı mətn şəklində yazın — "
            "qiymət, ərazi və xidmətlər haqqında kömək edə bilərəm."
        )
        send_result = _maybe_send(sender_igsid=sender_igsid, text=reply, credentials=creds)
        return {"ok": True, "type": "media_ack", "send": send_result}

    with transaction.atomic():
        conversation = _get_or_create_conversation(business, sender_igsid, creds)
        history = list(
            conversation.messages.filter(sender=MessageSender.CUSTOMER)
            .order_by("-timestamp")
            .values_list("content", flat=True)[:8]
        )
        history = list(reversed(history))

        Message.objects.create(
            conversation=conversation,
            sender=MessageSender.CUSTOMER,
            content=text,
        )

        result = get_responder().respond(
            business=business,
            message=text,
            history=history,
            conversation=conversation,
            source=LeadSource.INSTAGRAM,
        )

        if not getattr(result, "should_reply", True) or not (result.answer or "").strip():
            return {
                "ok": True,
                "sender": sender_igsid,
                "intent": result.detected_intent,
                "answer": "",
                "skipped_reply": True,
                "lead": False,
                "send": {"skipped": True, "reason": "off_topic"},
                "conversation_id": conversation.id,
            }

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

    send_result = _maybe_send(sender_igsid=sender_igsid, text=result.answer, credentials=creds)
    if send_result.get("error"):
        Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).update(
            last_error=str(send_result["error"])[:500]
        )
    else:
        Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).update(
            status=ChannelStatus.LIVE,
            last_error="",
        )

    return {
        "ok": True,
        "sender": sender_igsid,
        "intent": result.detected_intent,
        "answer": result.answer[:200],
        "lead": bool(result.lead_created),
        "send": send_result,
        "conversation_id": conversation.id,
    }

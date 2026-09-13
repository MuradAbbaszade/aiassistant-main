"""Outbound CRM webhook dispatch: sign, deliver, retry."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import threading
import uuid
from datetime import timedelta

import requests
from django.db import transaction
from django.utils import timezone

from businesses.models import Business, BusinessPlan
from integrations.models import DeliveryStatus, WebhookDelivery, WebhookEndpoint, WebhookEvent

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
REQUEST_TIMEOUT = 8
# attempt index → delay before next retry
RETRY_DELAYS_SECONDS = (0, 60, 300, 1800, 7200)


def lead_payload(lead) -> dict:
    return {
        "lead_id": lead.id,
        "name": lead.name,
        "phone": lead.contact,
        "intent": lead.intent,
        "source": lead.source,
        "status": lead.status,
        "conversation_id": lead.conversation_id,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
    }


def build_event_envelope(*, business: Business, event_type: str, data: dict) -> dict:
    return {
        "id": f"evt_{uuid.uuid4().hex}",
        "type": event_type,
        "created_at": timezone.now().isoformat(),
        "business_id": business.id,
        "data": data,
    }


def sign_payload(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def emit_event(*, business: Business | None, event_type: str, data: dict) -> list[WebhookDelivery]:
    """Queue webhook deliveries for active Biznes-plan endpoints."""
    if business is None:
        return []
    if business.plan != BusinessPlan.BUSINESS:
        return []

    endpoints = list(
        WebhookEndpoint.objects.filter(business=business, is_active=True).only(
            "id", "events", "url", "secret", "is_active"
        )
    )
    if not endpoints:
        return []

    envelope = build_event_envelope(business=business, event_type=event_type, data=data)
    deliveries: list[WebhookDelivery] = []
    for endpoint in endpoints:
        if not endpoint.listens_for(event_type):
            continue
        delivery = WebhookDelivery.objects.create(
            endpoint=endpoint,
            event_type=event_type,
            payload=envelope,
            status=DeliveryStatus.PENDING,
            next_retry_at=timezone.now(),
        )
        deliveries.append(delivery)
        _schedule_delivery(delivery.pk)
    return deliveries


def emit_lead_created(lead) -> list[WebhookDelivery]:
    return emit_event(
        business=lead.business,
        event_type=WebhookEvent.LEAD_CREATED,
        data=lead_payload(lead),
    )


def emit_lead_updated(lead) -> list[WebhookDelivery]:
    return emit_event(
        business=lead.business,
        event_type=WebhookEvent.LEAD_UPDATED,
        data=lead_payload(lead),
    )


def _schedule_delivery(delivery_id: int) -> None:
    def _run():
        try:
            process_delivery(delivery_id)
        except Exception:
            logger.exception("Webhook delivery crashed for id=%s", delivery_id)

    transaction.on_commit(lambda: threading.Thread(target=_run, daemon=True).start())


def process_delivery(delivery_id: int) -> bool:
    try:
        delivery = WebhookDelivery.objects.select_related("endpoint", "endpoint__business").get(
            pk=delivery_id
        )
    except WebhookDelivery.DoesNotExist:
        return False

    endpoint = delivery.endpoint
    if not endpoint.is_active:
        delivery.status = DeliveryStatus.FAILED
        delivery.last_error = "Endpoint inactive"
        delivery.save(update_fields=["status", "last_error", "updated_at"])
        return False

    if endpoint.business.plan != BusinessPlan.BUSINESS:
        delivery.status = DeliveryStatus.FAILED
        delivery.last_error = "Business plan does not include integrations"
        delivery.save(update_fields=["status", "last_error", "updated_at"])
        return False

    body = json.dumps(delivery.payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    signature = sign_payload(endpoint.secret, body)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AI-Assistant-Webhooks/1.0",
        "X-AI-Assistant-Event": delivery.event_type,
        "X-AI-Assistant-Delivery": str(delivery.id),
        "X-AI-Assistant-Signature": signature,
    }

    delivery.attempts += 1
    try:
        resp = requests.post(endpoint.url, data=body, headers=headers, timeout=REQUEST_TIMEOUT)
        delivery.response_code = resp.status_code
        delivery.response_body = (resp.text or "")[:2000]
        if 200 <= resp.status_code < 300:
            delivery.status = DeliveryStatus.SUCCESS
            delivery.next_retry_at = None
            delivery.last_error = ""
            delivery.save(
                update_fields=[
                    "attempts",
                    "response_code",
                    "response_body",
                    "status",
                    "next_retry_at",
                    "last_error",
                    "updated_at",
                ]
            )
            return True
        delivery.last_error = f"HTTP {resp.status_code}"
    except requests.RequestException as exc:
        delivery.response_code = None
        delivery.response_body = ""
        delivery.last_error = str(exc)[:500]

    if delivery.attempts >= MAX_ATTEMPTS:
        delivery.status = DeliveryStatus.FAILED
        delivery.next_retry_at = None
    else:
        delay = RETRY_DELAYS_SECONDS[min(delivery.attempts, len(RETRY_DELAYS_SECONDS) - 1)]
        delivery.status = DeliveryStatus.PENDING
        delivery.next_retry_at = timezone.now() + timedelta(seconds=delay)

    delivery.save(
        update_fields=[
            "attempts",
            "response_code",
            "response_body",
            "status",
            "next_retry_at",
            "last_error",
            "updated_at",
        ]
    )
    return False


def process_due_deliveries(*, limit: int = 50) -> int:
    """Retry pending deliveries whose next_retry_at is due. Returns processed count."""
    now = timezone.now()
    ids = list(
        WebhookDelivery.objects.filter(
            status=DeliveryStatus.PENDING,
            next_retry_at__lte=now,
        )
        .order_by("next_retry_at")
        .values_list("id", flat=True)[:limit]
    )
    ok = 0
    for delivery_id in ids:
        if process_delivery(delivery_id):
            ok += 1
    return ok


def send_test_event(endpoint: WebhookEndpoint) -> WebhookDelivery:
    payload = build_event_envelope(
        business=endpoint.business,
        event_type=WebhookEvent.LEAD_CREATED,
        data={
            "lead_id": 0,
            "name": "Test Lead",
            "phone": "+994701112233",
            "intent": "Webhook test",
            "source": "instagram",
            "status": "New",
            "conversation_id": None,
            "created_at": timezone.now().isoformat(),
            "updated_at": timezone.now().isoformat(),
            "test": True,
        },
    )
    delivery = WebhookDelivery.objects.create(
        endpoint=endpoint,
        event_type=WebhookEvent.LEAD_CREATED,
        payload=payload,
        status=DeliveryStatus.PENDING,
        next_retry_at=timezone.now(),
    )
    process_delivery(delivery.pk)
    delivery.refresh_from_db()
    return delivery

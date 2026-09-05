"""Meta Instagram webhook HTTP endpoints."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from channels.services.instagram import verify_webhook_signature
from channels.webhook_handlers import handle_instagram_webhook_payload

logger = logging.getLogger(__name__)
WEBHOOK_LOG = Path(settings.BASE_DIR) / "logs" / "instagram_webhooks.jsonl"


def _append_webhook_log(entry: dict) -> None:
    try:
        WEBHOOK_LOG.parent.mkdir(parents=True, exist_ok=True)
        with WEBHOOK_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception:
        logger.exception("Failed writing webhook log")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def instagram_webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        expected = getattr(settings, "META_VERIFY_TOKEN", "aikomekci_verify")
        _append_webhook_log(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "method": "GET",
                "query": dict(request.GET.items()),
                "ok": mode == "subscribe" and token == expected and bool(challenge),
            }
        )
        if mode == "subscribe" and token == expected and challenge:
            logger.info("Instagram webhook verified")
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponseForbidden("Verification failed")

    raw = request.body or b""
    sig = request.headers.get("X-Hub-Signature-256") or request.META.get("HTTP_X_HUB_SIGNATURE_256")
    if not verify_webhook_signature(raw, sig):
        logger.warning("Invalid Instagram webhook signature")
        _append_webhook_log(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "method": "POST",
                "error": "invalid_signature",
                "body_preview": raw[:500].decode("utf-8", errors="replace"),
            }
        )
        return HttpResponseForbidden("Invalid signature")

    try:
        payload = json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    logger.info("Instagram webhook received: object=%s", payload.get("object"))
    result = handle_instagram_webhook_payload(payload)
    _append_webhook_log(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "method": "POST",
            "object": payload.get("object"),
            "payload": payload,
            "result": result,
        }
    )
    return JsonResponse({"status": "ok", **result})

from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.decorators import demo_login_required
from integrations.models import DEFAULT_WEBHOOK_EVENTS, WebhookDelivery, WebhookEndpoint, WebhookEvent
from integrations.services.dispatch import process_due_deliveries, send_test_event


def _require_business(request):
    business = getattr(request, "current_business", None)
    if business is None:
        return None, redirect("accounts:onboarding")
    return business, None


@demo_login_required
def integrations_home(request):
    business, early = _require_business(request)
    if early:
        return early

    process_due_deliveries(limit=20)

    if not business.has_integrations:
        return render(
            request,
            "dashboard/integrations_locked.html",
            {"active_nav": "integrations", "business": business},
        )

    endpoints = WebhookEndpoint.objects.filter(business=business)
    deliveries = (
        WebhookDelivery.objects.filter(endpoint__business=business)
        .select_related("endpoint")
        .order_by("-created_at")[:30]
    )
    return render(
        request,
        "dashboard/integrations.html",
        {
            "active_nav": "integrations",
            "business": business,
            "endpoints": endpoints,
            "deliveries": deliveries,
            "event_choices": list(WebhookEvent),
        },
    )


@demo_login_required
@require_http_methods(["POST"])
def endpoint_create(request):
    business, early = _require_business(request)
    if early:
        return early
    if not business.has_integrations:
        messages.error(request, "Biznes plan required.")
        return redirect("integrations:home")

    name = (request.POST.get("name") or "CRM webhook").strip()[:120]
    url = (request.POST.get("url") or "").strip()
    if not url.startswith(("http://", "https://")):
        messages.error(request, "Valid HTTPS webhook URL required.")
        return redirect("integrations:home")

    selected = request.POST.getlist("events")
    allowed = {e.value for e in WebhookEvent}
    events = [e for e in selected if e in allowed] or list(DEFAULT_WEBHOOK_EVENTS)

    WebhookEndpoint.objects.create(
        business=business,
        name=name or "CRM webhook",
        url=url,
        events=events,
        is_active=True,
    )
    messages.success(request, "Webhook endpoint saved.")
    return redirect("integrations:home")


@demo_login_required
@require_http_methods(["POST"])
def endpoint_toggle(request, pk: int):
    business, early = _require_business(request)
    if early:
        return early
    if not business.has_integrations:
        return redirect("integrations:home")

    endpoint = get_object_or_404(WebhookEndpoint, pk=pk, business=business)
    endpoint.is_active = not endpoint.is_active
    endpoint.save(update_fields=["is_active", "updated_at"])
    messages.success(request, "Webhook updated.")
    return redirect("integrations:home")


@demo_login_required
@require_http_methods(["POST"])
def endpoint_delete(request, pk: int):
    business, early = _require_business(request)
    if early:
        return early
    if not business.has_integrations:
        return redirect("integrations:home")

    endpoint = get_object_or_404(WebhookEndpoint, pk=pk, business=business)
    endpoint.delete()
    messages.success(request, "Webhook deleted.")
    return redirect("integrations:home")


@demo_login_required
@require_http_methods(["POST"])
def endpoint_test(request, pk: int):
    business, early = _require_business(request)
    if early:
        return early
    if not business.has_integrations:
        return redirect("integrations:home")

    endpoint = get_object_or_404(WebhookEndpoint, pk=pk, business=business)
    delivery = send_test_event(endpoint)
    if delivery.status == "success":
        messages.success(request, "Test webhook delivered successfully.")
    else:
        messages.error(
            request,
            f"Test webhook failed: {delivery.last_error or delivery.response_code or 'unknown'}",
        )
    return redirect("integrations:home")


@demo_login_required
@require_http_methods(["POST"])
def delivery_retry(request, pk: int):
    business, early = _require_business(request)
    if early:
        return early
    if not business.has_integrations:
        return redirect("integrations:home")

    delivery = get_object_or_404(WebhookDelivery, pk=pk, endpoint__business=business)
    from django.utils import timezone

    from integrations.models import DeliveryStatus
    from integrations.services.dispatch import process_delivery

    delivery.status = DeliveryStatus.PENDING
    delivery.next_retry_at = timezone.now()
    delivery.save(update_fields=["status", "next_retry_at", "updated_at"])
    process_delivery(delivery.pk)
    messages.success(request, "Delivery retried.")
    return redirect("integrations:home")

import json

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from channels.models import Channel, ChannelStatus, ChannelType
from channels.services.instagram import get_credentials_for_business, send_instagram_text
from channels.services.oauth import get_oauth_redirect_uri, subscribe_instagram_webhooks
from channels.webhook_handlers import handle_instagram_webhook_payload
from channels.webhooks import WEBHOOK_LOG
from conversations.models import Conversation, Message
from core.decorators import demo_login_required


def _is_real_instagram_thread(conv: Conversation) -> bool:
    uid = (conv.external_user_id or "").strip()
    if not uid or uid.startswith("SIMULATED"):
        return False
    if conv.customer_name == "Demo Müştəri":
        return False
    return uid.isdigit()


@demo_login_required
def channel_list(request):
    business = request.current_business
    channels = Channel.objects.filter(business=business) if business else []
    ig = None
    real_threads = []
    demo_threads = []
    real_messages = []
    demo_messages = []
    if business:
        ig = Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).first()
        all_threads = list(
            Conversation.objects.filter(business=business, channel="instagram")
            .prefetch_related("messages")
            .order_by("-updated_at")[:30]
        )
        for t in all_threads:
            if _is_real_instagram_thread(t):
                real_threads.append(t)
            else:
                demo_threads.append(t)

        all_msgs = (
            Message.objects.filter(conversation__business=business, conversation__channel="instagram")
            .select_related("conversation")
            .order_by("-timestamp")[:60]
        )
        for m in all_msgs:
            if _is_real_instagram_thread(m.conversation):
                real_messages.append(m)
            else:
                demo_messages.append(m)

    public_base = getattr(settings, "PUBLIC_BASE_URL", "") or ""
    webhook_url = f"{public_base.rstrip('/')}/webhooks/instagram/" if public_base else "/webhooks/instagram/"

    recent_hooks = []
    post_hooks = 0
    if WEBHOOK_LOG.exists():
        lines = WEBHOOK_LOG.read_text(encoding="utf-8").strip().splitlines()[-40:]
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                recent_hooks.append(entry)
                if entry.get("method") == "POST":
                    post_hooks += 1
            except json.JSONDecodeError:
                continue

    return render(
        request,
        "dashboard/channels.html",
        {
            "channels": channels,
            "ig_channel": ig,
            "active_nav": "channels",
            "instagram_live": bool(ig and ig.is_live),
            "webhook_url": webhook_url,
            "public_base_url": public_base,
            "redirect_uri": get_oauth_redirect_uri(),
            "verify_token": getattr(settings, "META_VERIFY_TOKEN", "aikomekci_verify"),
            "recent_hooks": recent_hooks,
            "real_threads": real_threads,
            "demo_threads": demo_threads,
            "real_messages": real_messages,
            "demo_messages": demo_messages,
            "webhook_post_count": post_hooks,
        },
    )


@demo_login_required
@require_http_methods(["POST"])
def instagram_connect(request):
    return redirect("accounts:instagram_login")


@demo_login_required
@require_http_methods(["POST"])
def instagram_disconnect(request):
    business = request.current_business
    channel = Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).first()
    if channel:
        channel.access_token = ""
        channel.status = ChannelStatus.DISCONNECTED
        channel.last_error = ""
        channel.save(update_fields=["access_token", "status", "last_error", "updated_at"])
        messages.info(request, "Instagram bağlantısı kəsildi. Yenidən OAuth ilə qoşula bilərsiniz.")
    return redirect("channels:list")


@demo_login_required
@require_http_methods(["POST"])
def instagram_resubscribe(request):
    business = request.current_business
    channel = Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).first()
    if not channel or not channel.access_token:
        messages.error(request, "Canlı Instagram tokeni yoxdur.")
        return redirect("channels:list")
    result = subscribe_instagram_webhooks(channel.access_token, channel.external_id)
    if result.get("success"):
        messages.success(request, "Webhook subscription yeniləndi (messages).")
        channel.last_error = ""
        channel.save(update_fields=["last_error", "updated_at"])
    else:
        messages.error(request, f"Subscribe xətası: {result}")
        channel.last_error = str(result)[:500]
        channel.save(update_fields=["last_error", "updated_at"])
    return redirect("channels:list")


@demo_login_required
@require_http_methods(["POST"])
def instagram_simulate_webhook(request):
    business = request.current_business
    channel = Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).first()
    text = (request.POST.get("text") or "Salam, qiymet neceye?").strip()
    if not channel or not channel.external_id:
        messages.error(request, "Instagram channel yoxdur.")
        return redirect("channels:list")
    payload = {
        "object": "instagram",
        "entry": [
            {
                "id": channel.external_id,
                "time": 1,
                "messaging": [
                    {
                        "sender": {"id": "SIMULATED_SENDER_IGSID"},
                        "recipient": {"id": channel.external_id},
                        "timestamp": 1,
                        "message": {"mid": "sim-mid", "text": text},
                    }
                ],
            }
        ],
    }
    result = handle_instagram_webhook_payload(payload)
    messages.info(request, f"Simulyasiya nəticəsi: {result}")
    return redirect("channels:list")


@demo_login_required
@require_http_methods(["POST"])
def instagram_test_send(request):
    igsid = (request.POST.get("igsid") or "").strip()
    text = (request.POST.get("text") or "Hello! AI Assistant test message.").strip()
    business = request.current_business
    if not igsid:
        messages.error(request, "IGSID lazımdır (müştəri sizə DM yazdıqdan sonra webhook-dan gəlir).")
        return redirect("channels:list")
    creds = get_credentials_for_business(business.id) if business else None
    if not creds:
        messages.error(request, "Bu biznes üçün Instagram tokeni yoxdur — yenidən daxil olun.")
        return redirect("channels:list")
    try:
        send_instagram_text(recipient_igsid=igsid, text=text, credentials=creds)
        messages.success(request, "Test mesajı Instagram-a göndərildi.")
        Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).update(
            status=ChannelStatus.LIVE, last_error=""
        )
    except Exception as exc:
        messages.error(request, f"Göndərmə xətası: {exc}")
        Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).update(
            last_error=str(exc)[:500]
        )
    return redirect("channels:list")

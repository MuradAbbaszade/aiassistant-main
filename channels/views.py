from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from channels.models import Channel, ChannelStatus, ChannelType
from channels.services.instagram import get_credentials_for_business, send_instagram_text
from channels.services.oauth import subscribe_instagram_webhooks
from channels.webhook_handlers import handle_instagram_webhook_payload
from conversations.models import Conversation, Message
from core.decorators import demo_login_required


def _is_real_instagram_thread(conv: Conversation) -> bool:
    uid = (conv.external_user_id or "").strip()
    if not uid or uid.startswith("SIMULATED"):
        return False
    if conv.customer_name in ("Demo Müştəri", "Demo Customer"):
        return False
    return uid.isdigit()


@demo_login_required
def channel_list(request):
    business = request.current_business
    channels = list(Channel.objects.filter(business=business)) if business else []
    ig = None
    real_messages = []
    if business:
        ig = Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).first()
        all_msgs = (
            Message.objects.filter(conversation__business=business, conversation__channel="instagram")
            .select_related("conversation")
            .order_by("-timestamp")[:40]
        )
        real_messages = [m for m in all_msgs if _is_real_instagram_thread(m.conversation)]

    other_channels = [ch for ch in channels if ch.type != ChannelType.INSTAGRAM]

    return render(
        request,
        "dashboard/channels.html",
        {
            "ig_channel": ig,
            "other_channels": other_channels,
            "active_nav": "channels",
            "real_messages": real_messages,
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
        messages.info(request, "Instagram bağlantısı kəsildi. İstəyəndə yenidən qoşa bilərsiniz.")
    return redirect("channels:list")


@demo_login_required
@require_http_methods(["POST"])
def instagram_resubscribe(request):
    business = request.current_business
    channel = Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).first()
    if not channel or not channel.access_token:
        messages.error(request, "Əvvəlcə Instagram hesabınızı qoşun.")
        return redirect("channels:list")
    result = subscribe_instagram_webhooks(channel.access_token, channel.external_id)
    if result.get("success"):
        messages.success(request, "Mesaj qəbulu yeniləndi.")
        channel.last_error = ""
        channel.save(update_fields=["last_error", "updated_at"])
    else:
        messages.error(request, "Mesaj qəbulunu yeniləmək alınmadı. Yenidən qoşulmağı yoxlayın.")
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
        messages.error(request, "Instagram hesabı tapılmadı.")
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
    handle_instagram_webhook_payload(payload)
    messages.info(request, "Test söhbəti yaradıldı. Söhbətlər bölməsinə baxın.")
    return redirect("channels:list")


@demo_login_required
@require_http_methods(["POST"])
def instagram_test_send(request):
    igsid = (request.POST.get("igsid") or "").strip()
    text = (request.POST.get("text") or "Salam! AI Assistant test mesajı.").strip()
    business = request.current_business
    if not igsid:
        messages.error(request, "Müştəri ID lazımdır. Əvvəlcə müştəri sizə yazmalıdır.")
        return redirect("channels:list")
    creds = get_credentials_for_business(business.id) if business else None
    if not creds:
        messages.error(request, "Instagram qoşulmayıb — yenidən daxil olun.")
        return redirect("channels:list")
    try:
        send_instagram_text(recipient_igsid=igsid, text=text, credentials=creds)
        messages.success(request, "Mesaj Instagram-a göndərildi.")
        Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).update(
            status=ChannelStatus.LIVE, last_error=""
        )
    except Exception as exc:
        messages.error(request, f"Göndərmə alınmadı: {exc}")
        Channel.objects.filter(business=business, type=ChannelType.INSTAGRAM).update(
            last_error=str(exc)[:500]
        )
    return redirect("channels:list")

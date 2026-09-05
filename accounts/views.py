from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ai.models import AISettings
from channels.models import Channel, ChannelStatus
from channels.services.oauth import (
    build_authorize_url,
    complete_oauth,
    get_oauth_redirect_uri,
    new_oauth_state,
    upsert_business_from_oauth,
)
from conversations.models import Conversation
from core.i18n import get_translator
from knowledge.models import KnowledgeItem


def login_view(request):
    """Instagram OAuth is the only login method."""
    if request.session.get("demo_logged_in") and request.session.get("current_business_id"):
        return redirect("analytics:dashboard")

    error = request.GET.get("error") or request.session.pop("oauth_error", None)
    return render(
        request,
        "accounts/login.html",
        {
            "error": error,
            "redirect_uri": get_oauth_redirect_uri(),
        },
    )


@require_http_methods(["GET"])
def instagram_login_start(request):
    try:
        state = new_oauth_state()
        request.session["ig_oauth_state"] = state
        url = build_authorize_url(state=state)
        return redirect(url)
    except Exception as exc:
        messages.error(request, f"Instagram login başladılmadı: {exc}")
        return redirect("accounts:login")


@require_http_methods(["GET"])
def instagram_callback(request):
    err = request.GET.get("error")
    if err:
        desc = request.GET.get("error_description") or err
        request.session["oauth_error"] = f"Instagram icazə verilmədi: {desc}"
        return redirect("accounts:login")

    state = request.GET.get("state") or ""
    expected = request.session.pop("ig_oauth_state", "")
    if not state or state != expected:
        request.session["oauth_error"] = "OAuth state uyğunsuzdur. Yenidən cəhd edin."
        return redirect("accounts:login")

    code = request.GET.get("code")
    if not code:
        request.session["oauth_error"] = "Instagram authorization code gəlmədi."
        return redirect("accounts:login")

    try:
        result = complete_oauth(code)
        business, channel, created = upsert_business_from_oauth(result)
    except Exception as exc:
        request.session["oauth_error"] = f"Token alınmadı: {exc}"
        return redirect("accounts:login")

    request.session["demo_logged_in"] = True
    request.session["demo_user_email"] = f"@{result.username}"
    request.session["demo_user_name"] = result.name or result.username
    request.session["current_business_id"] = business.id
    request.session["instagram_user_id"] = result.user_id
    request.session.pop("demo_conversation_id", None)

    if created:
        messages.success(
            request,
            f"@{result.username} qoşuldu. Biznes məlumatlarınızı yazın — AI Instagram DM-lərə cavab verəcək.",
        )
        return redirect("accounts:onboarding")
    messages.success(request, f"@{result.username} hesabına daxil oldunuz.")
    return redirect("analytics:dashboard")


def logout_view(request):
    request.session.flush()
    return redirect("marketing:landing")


def onboarding_view(request):
    if not request.session.get("demo_logged_in"):
        return redirect("accounts:login")

    business = getattr(request, "current_business", None)
    ig_connected = False
    kb_ready = False
    ai_ready = False
    has_messages = False

    if business:
        ig_connected = Channel.objects.filter(
            business=business,
            type="instagram",
            status__in=[ChannelStatus.LIVE, ChannelStatus.CONNECTED],
        ).exclude(access_token="").exists()
        kb_ready = KnowledgeItem.objects.filter(business=business).exists()
        ai = AISettings.objects.filter(business=business).first()
        ai_ready = bool(ai and (ai.rules or "").strip())
        has_messages = Conversation.objects.filter(business=business).exists()

    tr = get_translator(getattr(request, "ui_lang", None))
    steps = [
        {"title": tr["onb.s1"], "desc": tr["onb.s1d"], "done": ig_connected},
        {"title": tr["onb.s2"], "desc": tr["onb.s2d"], "done": kb_ready},
        {"title": tr["onb.s3"], "desc": tr["onb.s3d"], "done": ai_ready},
        {"title": tr["onb.s4"], "desc": tr["onb.s4d"], "done": has_messages},
        {"title": tr["onb.s5"], "desc": tr["onb.s5d"], "done": has_messages},
    ]
    return render(request, "accounts/onboarding.html", {"steps": steps})

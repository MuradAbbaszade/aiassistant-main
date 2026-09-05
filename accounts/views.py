from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from channels.services.oauth import (
    build_authorize_url,
    complete_oauth,
    get_oauth_redirect_uri,
    new_oauth_state,
    upsert_business_from_oauth,
)


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
            f"@{result.username} qoşuldu. Knowledge Base doldurun — AI Instagram DM-lərə cavab verəcək.",
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
    steps = [
        {
            "title": "Instagram qoşuldu",
            "desc": "Hesabınız OAuth ilə bağlandı — mesaj göndərmə icazəsi alındı.",
            "done": True,
        },
        {
            "title": "Knowledge Base",
            "desc": "Xidmətlər, qiymət və FAQ əlavə edin ki, AI düzgün cavab versin.",
            "done": False,
        },
        {
            "title": "AI Settings",
            "desc": "Ton, dil və qaydaları tənzimləyin.",
            "done": False,
        },
        {
            "title": "Webhook",
            "desc": "Meta App-də /webhooks/instagram/ URL-ini yoxlayın (bir dəfəlik platform setup).",
            "done": False,
        },
        {
            "title": "Test DM",
            "desc": "Başqa IG hesabından öz biznes profilinizə yazın.",
            "done": False,
        },
    ]
    return render(request, "accounts/onboarding.html", {"steps": steps})

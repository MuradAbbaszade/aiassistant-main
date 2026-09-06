from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.forms import LoginForm, OTPForm, RegisterForm
from accounts.models import UserProfile, default_whatsapp_url
from accounts.services.otp import (
    OTP_RESEND_COOLDOWN_SECONDS,
    create_email_otp,
    send_otp_email,
    verify_otp,
)
from channels.models import Channel, ChannelStatus, ChannelType
from channels.services.oauth import (
    build_authorize_url,
    complete_oauth,
    new_oauth_state,
    upsert_business_from_oauth,
)


def _establish_session(request, user, business=None):
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    request.session["demo_logged_in"] = True
    request.session["demo_user_email"] = user.email
    request.session["demo_user_name"] = user.get_full_name() or user.email
    profile = getattr(user, "profile", None)
    biz = business or (profile.business if profile else None)
    if biz:
        request.session["current_business_id"] = biz.id
    request.session.pop("demo_conversation_id", None)
    request.session.pop("otp_sent_at", None)


def _post_login_redirect(user):
    profile = getattr(user, "profile", None)
    if profile and profile.business_id:
        ig = Channel.objects.filter(
            business=profile.business,
            type=ChannelType.INSTAGRAM,
            status__in=[ChannelStatus.LIVE, ChannelStatus.CONNECTED],
        ).exclude(access_token="").exists()
        if ig:
            return redirect("analytics:dashboard")
    return redirect("accounts:onboarding")


def _otp_resend_wait_seconds(request) -> int:
    sent_at = request.session.get("otp_sent_at")
    if not sent_at:
        return 0
    try:
        sent_ts = float(sent_at)
    except (TypeError, ValueError):
        return 0
    elapsed = timezone.now().timestamp() - sent_ts
    remaining = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
    return max(0, remaining)


def _start_otp(request, user, *, force: bool = False):
    """Create OTP and attempt email send without blocking the HTTP request forever."""
    wait = _otp_resend_wait_seconds(request)
    if not force and wait > 0:
        messages.info(
            request,
            f"Yeni kod göndərmək üçün {wait} saniyə gözləyin.",
        )
        return redirect("accounts:verify_email")

    otp = create_email_otp(user)
    request.session["pending_otp_user_id"] = user.id
    request.session["otp_sent_at"] = timezone.now().timestamp()
    from django.conf import settings

    try:
        ok, detail = send_otp_email(user, otp)
    except Exception:
        ok, detail = False, otp.code if settings.DEBUG else ""

    if ok:
        messages.success(request, "Emailinizə təsdiq kodu göndərildi.")
    elif detail:
        messages.info(request, f"Email göndərilmədi. Test OTP kodunuz: {detail}")
    else:
        messages.error(
            request,
            "Email göndərilmədi. Bir az sonra «Kodu yenidən göndər» edin.",
        )
    if settings.DEBUG:
        messages.info(request, f"DEBUG OTP: {otp.code}")
    return redirect("accounts:verify_email")


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated or request.session.get("demo_logged_in"):
        return _post_login_redirect(request.user) if request.user.is_authenticated else redirect(
            "accounts:onboarding"
        )

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=form.cleaned_data["password"],
            first_name=form.cleaned_data["first_name"].strip(),
            last_name=form.cleaned_data["last_name"].strip(),
            is_active=True,
        )
        UserProfile.objects.create(
            user=user,
            phone=form.cleaned_data.get("phone") or "",
            email_verified=False,
        )
        return _start_otp(request, user)

    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return _post_login_redirect(request.user)
    if request.session.get("demo_logged_in") and request.session.get("current_business_id"):
        return redirect("analytics:dashboard")

    form = LoginForm(request.POST or None)
    error = request.GET.get("error") or request.session.pop("oauth_error", None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].strip().lower()
        password = form.cleaned_data["password"]
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            form.add_error(None, "Email və ya şifrə yanlışdır.")
        else:
            authed = authenticate(request, username=user.username, password=password)
            if not authed:
                form.add_error(None, "Email və ya şifrə yanlışdır.")
            else:
                profile, _ = UserProfile.objects.get_or_create(user=authed)
                if not profile.email_verified:
                    return _start_otp(request, authed)
                _establish_session(request, authed)
                return _post_login_redirect(authed)

    return render(
        request,
        "accounts/login.html",
        {"form": form, "error": error},
    )


@require_http_methods(["GET", "POST"])
def verify_email_view(request):
    user_id = request.session.get("pending_otp_user_id")
    if not user_id:
        return redirect("accounts:login")
    user = User.objects.filter(pk=user_id).first()
    if not user:
        request.session.pop("pending_otp_user_id", None)
        return redirect("accounts:register")

    form = OTPForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if verify_otp(user, form.cleaned_data["code"]):
            request.session.pop("pending_otp_user_id", None)
            _establish_session(request, user)
            messages.success(request, "Email təsdiqləndi. Xoş gəldiniz!")
            return redirect("accounts:onboarding")
        form.add_error("code", "Kod yanlışdır və ya vaxtı bitib.")

    return render(
        request,
        "accounts/verify_otp.html",
        {"form": form, "email": user.email},
    )


@require_http_methods(["POST"])
def resend_otp_view(request):
    user_id = request.session.get("pending_otp_user_id")
    user = User.objects.filter(pk=user_id).first() if user_id else None
    if not user:
        return redirect("accounts:login")
    return _start_otp(request, user)


def onboarding_view(request):
    if not (request.user.is_authenticated or request.session.get("demo_logged_in")):
        return redirect("accounts:login")

    profile = getattr(request.user, "profile", None) if request.user.is_authenticated else None
    ig_connected = False
    if profile and profile.business_id:
        ig_connected = Channel.objects.filter(
            business=profile.business,
            type=ChannelType.INSTAGRAM,
            status__in=[ChannelStatus.LIVE, ChannelStatus.CONNECTED],
        ).exclude(access_token="").exists()
        if ig_connected:
            return redirect("analytics:dashboard")

    return render(
        request,
        "accounts/onboarding.html",
        {
            "whatsapp_url": default_whatsapp_url(),
            "user_name": (
                request.user.get_full_name()
                if request.user.is_authenticated
                else request.session.get("demo_user_name", "")
            ),
        },
    )


@require_http_methods(["POST"])
def onboarding_message_us(request):
    if not (request.user.is_authenticated or request.session.get("demo_logged_in")):
        return redirect("accounts:login")
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.onboarding_path = UserProfile.OnboardingPath.MESSAGE
        profile.save(update_fields=["onboarding_path", "updated_at"])
    return redirect(default_whatsapp_url())


@require_http_methods(["GET"])
def onboarding_manual(request):
    if not (request.user.is_authenticated or request.session.get("demo_logged_in")):
        messages.info(request, "Əvvəlcə hesabınıza daxil olun.")
        return redirect("accounts:login")
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.onboarding_path = UserProfile.OnboardingPath.MANUAL
        profile.save(update_fields=["onboarding_path", "updated_at"])
    return redirect("accounts:instagram_login")


@require_http_methods(["GET"])
def instagram_login_start(request):
    if not (request.user.is_authenticated or request.session.get("demo_logged_in")):
        messages.info(request, "Instagram qoşmaq üçün əvvəlcə hesabınıza daxil olun.")
        return redirect("accounts:login")
    try:
        state = new_oauth_state()
        request.session["ig_oauth_state"] = state
        url = build_authorize_url(state=state)
        return redirect(url)
    except Exception as exc:
        messages.error(request, f"Instagram login başladılmadı: {exc}")
        return redirect("accounts:onboarding")


@require_http_methods(["GET"])
def instagram_callback(request):
    err = request.GET.get("error")
    if err:
        desc = request.GET.get("error_description") or err
        request.session["oauth_error"] = f"Instagram icazə verilmədi: {desc}"
        return redirect("accounts:onboarding")

    if not (request.user.is_authenticated or request.session.get("demo_logged_in")):
        request.session["oauth_error"] = "Sessiya bitib. Yenidən daxil olun."
        return redirect("accounts:login")

    state = request.GET.get("state") or ""
    expected = request.session.pop("ig_oauth_state", "")
    if not state or state != expected:
        request.session["oauth_error"] = "OAuth state uyğunsuzdur. Yenidən cəhd edin."
        return redirect("accounts:onboarding")

    code = request.GET.get("code")
    if not code:
        request.session["oauth_error"] = "Instagram authorization code gəlmədi."
        return redirect("accounts:onboarding")

    try:
        result = complete_oauth(code)
        business, channel, created = upsert_business_from_oauth(result)
    except Exception as exc:
        request.session["oauth_error"] = f"Token alınmadı: {exc}"
        return redirect("accounts:onboarding")

    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.business_id and profile.business_id != business.id:
            # Keep the user's existing business; move/update Instagram channel onto it
            target = profile.business
            Channel.objects.update_or_create(
                business=target,
                type=ChannelType.INSTAGRAM,
                defaults={
                    "status": ChannelStatus.LIVE,
                    "handle": channel.handle,
                    "external_id": channel.external_id,
                    "access_token": channel.access_token,
                    "token_expires_at": channel.token_expires_at,
                    "last_error": "",
                },
            )
            if created:
                # Clean up auto-created empty business shell if unused
                if not Channel.objects.filter(business=business).exclude(type=ChannelType.INSTAGRAM).exists():
                    pass
            business = target
        profile.business = business
        profile.onboarding_path = UserProfile.OnboardingPath.MANUAL
        profile.save(update_fields=["business", "onboarding_path", "updated_at"])
        _establish_session(request, request.user, business=business)
    else:
        request.session["demo_logged_in"] = True
        request.session["demo_user_email"] = f"@{result.username}"
        request.session["demo_user_name"] = result.name or result.username
        request.session["current_business_id"] = business.id

    request.session["instagram_user_id"] = result.user_id
    messages.success(
        request,
        f"@{result.username} qoşuldu. İndi biznes məlumatlarınızı əlavə edə bilərsiniz.",
    )
    return redirect("analytics:dashboard")


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect("marketing:landing")

from __future__ import annotations

import logging
import secrets
import socket
from datetime import timedelta

import requests
from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.utils import timezone

from accounts.models import EmailOTP

logger = logging.getLogger(__name__)

OTP_TTL_MINUTES = 10
EMAIL_SEND_TIMEOUT = 8
OTP_RESEND_COOLDOWN_SECONDS = 120


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_email_otp(user) -> EmailOTP:
    EmailOTP.objects.filter(user=user, used=False).update(used=True)
    return EmailOTP.objects.create(
        user=user,
        code=generate_otp_code(),
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )


def _otp_body(user, otp: EmailOTP) -> tuple[str, str]:
    subject = "AI Assistant — email verification code"
    body = (
        f"Salam {user.first_name or ''},\n\n"
        f"Your verification code is: {otp.code}\n\n"
        f"It expires in {OTP_TTL_MINUTES} minutes.\n\n"
        f"— AI Assistant"
    )
    return subject, body


def _from_email() -> str:
    return getattr(settings, "DEFAULT_FROM_EMAIL", None) or "AI Assistant <onboarding@resend.dev>"


def _send_via_resend(to_email: str, subject: str, body: str) -> bool:
    """HTTPS API — works on Render (SMTP ports are often blocked)."""
    api_key = (getattr(settings, "RESEND_API_KEY", "") or "").strip()
    if not api_key:
        return False
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": _from_email(),
            "to": [to_email],
            "subject": subject,
            "text": body,
        },
        timeout=EMAIL_SEND_TIMEOUT,
    )
    if resp.status_code >= 400:
        logger.error("Resend API error %s: %s", resp.status_code, resp.text[:500])
        resp.raise_for_status()
    return True


def _send_via_brevo(to_email: str, subject: str, body: str) -> bool:
    """Brevo (Sendinblue) HTTPS API — also works on Render."""
    api_key = (getattr(settings, "BREVO_API_KEY", "") or "").strip()
    if not api_key:
        return False
    sender_email = getattr(settings, "BREVO_SENDER_EMAIL", "") or ""
    # Parse "Name <email@x.com>" if needed
    from_addr = _from_email()
    name = "AI Assistant"
    email = sender_email
    if "<" in from_addr and ">" in from_addr:
        name = from_addr.split("<", 1)[0].strip() or name
        email = email or from_addr.split("<", 1)[1].rstrip(">").strip()
    if not email:
        email = from_addr
    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "sender": {"name": name, "email": email},
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": body,
        },
        timeout=EMAIL_SEND_TIMEOUT,
    )
    if resp.status_code >= 400:
        logger.error("Brevo API error %s: %s", resp.status_code, resp.text[:500])
        resp.raise_for_status()
    return True


def _send_via_smtp(to_email: str, subject: str, body: str) -> bool:
    timeout = int(getattr(settings, "EMAIL_TIMEOUT", EMAIL_SEND_TIMEOUT) or EMAIL_SEND_TIMEOUT)
    previous_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        connection = get_connection(timeout=timeout)
        sent = send_mail(
            subject,
            body,
            _from_email(),
            [to_email],
            connection=connection,
            fail_silently=False,
        )
        return bool(sent)
    finally:
        socket.setdefaulttimeout(previous_timeout)


def send_otp_email(user, otp: EmailOTP) -> tuple[bool, str]:
    """Send OTP via HTTPS email API when possible (Render blocks SMTP).

    Returns (ok, detail). detail may include OTP code in DEBUG.
    """
    subject, body = _otp_body(user, otp)
    to_email = user.email

    # 1) Prefer HTTPS providers (Render-compatible)
    for name, sender in (
        ("Resend", _send_via_resend),
        ("Brevo", _send_via_brevo),
    ):
        api_configured = (
            (name == "Resend" and (getattr(settings, "RESEND_API_KEY", "") or "").strip())
            or (name == "Brevo" and (getattr(settings, "BREVO_API_KEY", "") or "").strip())
        )
        if not api_configured:
            continue
        try:
            if sender(to_email, subject, body):
                logger.info("OTP email sent via %s to %s", name, to_email)
                return True, ""
        except Exception as exc:
            logger.exception("OTP email via %s failed for %s: %s", name, to_email, exc)

    # 2) SMTP (often blocked on Render free/web — Errno 101 Network unreachable)
    if (getattr(settings, "EMAIL_HOST", "") or "").strip():
        try:
            if _send_via_smtp(to_email, subject, body):
                return True, ""
        except OSError as exc:
            logger.exception(
                "OTP SMTP failed for %s (Render often blocks SMTP ports): %s. "
                "Set RESEND_API_KEY instead.",
                to_email,
                exc,
            )
        except Exception as exc:
            logger.exception("OTP email failed for %s: %s", to_email, exc)
    else:
        logger.info("OTP for %s (no email provider): %s", to_email, otp.code)
        try:
            send_mail(subject, body, _from_email(), [to_email], fail_silently=True)
        except Exception:
            pass

    if settings.DEBUG:
        return False, otp.code
    return False, ""


def verify_otp(user, code: str) -> bool:
    code = (code or "").strip()
    otp = (
        EmailOTP.objects.filter(user=user, used=False, code=code)
        .order_by("-created_at")
        .first()
    )
    if not otp or not otp.is_valid:
        return False
    otp.used = True
    otp.save(update_fields=["used"])
    profile = getattr(user, "profile", None)
    if profile:
        profile.email_verified = True
        profile.save(update_fields=["email_verified", "updated_at"])
    return True

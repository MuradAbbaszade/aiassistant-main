from __future__ import annotations

import logging
import secrets
import socket
from datetime import timedelta

from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.utils import timezone

from accounts.models import EmailOTP

logger = logging.getLogger(__name__)

OTP_TTL_MINUTES = 10
EMAIL_SEND_TIMEOUT = 8


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_email_otp(user) -> EmailOTP:
    EmailOTP.objects.filter(user=user, used=False).update(used=True)
    return EmailOTP.objects.create(
        user=user,
        code=generate_otp_code(),
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )


def send_otp_email(user, otp: EmailOTP) -> tuple[bool, str]:
    """Send OTP email quickly. Never block the request for long SMTP waits.

    Returns (ok, detail). detail may include the OTP code when email cannot be sent
    and DEBUG is on (or EMAIL_HOST is empty).
    """
    subject = "AI Assistant — email verification code"
    body = (
        f"Salam {user.first_name or ''},\n\n"
        f"Your verification code is: {otp.code}\n\n"
        f"It expires in {OTP_TTL_MINUTES} minutes.\n\n"
        f"— AI Assistant"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "noreply@aiassistant.local"
    timeout = int(getattr(settings, "EMAIL_TIMEOUT", EMAIL_SEND_TIMEOUT) or EMAIL_SEND_TIMEOUT)

    # No SMTP configured → console / show code in DEBUG
    if not (getattr(settings, "EMAIL_HOST", "") or "").strip():
        logger.info("OTP for %s (no EMAIL_HOST): %s", user.email, otp.code)
        try:
            send_mail(subject, body, from_email, [user.email], fail_silently=True)
        except Exception:
            logger.exception("Console email failed")
        return (False, otp.code) if settings.DEBUG else (True, "")

    previous_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        connection = get_connection(timeout=timeout)
        sent = send_mail(
            subject,
            body,
            from_email,
            [user.email],
            connection=connection,
            fail_silently=False,
        )
        if sent:
            return True, ""
    except Exception as exc:
        logger.exception("OTP email failed for %s: %s", user.email, exc)
        # Allow local/dev recovery; avoid leaking OTP in production toasts
        if settings.DEBUG:
            return False, otp.code
        return False, ""
    finally:
        socket.setdefaulttimeout(previous_timeout)

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

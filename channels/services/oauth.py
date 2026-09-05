"""
Business Login for Instagram (OAuth).

Flow:
1. GET /auth/instagram/ → redirect to Instagram authorize
2. User grants instagram_business_basic + manage_messages
3. GET /auth/instagram/callback/?code=... → exchange tokens → create Business + Channel
"""
from __future__ import annotations

import logging
import re
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from ai.models import AISettings
from businesses.models import Business, BusinessType
from channels.models import Channel, ChannelStatus, ChannelType

logger = logging.getLogger(__name__)

DEFAULT_SCOPES = (
    "instagram_business_basic,"
    "instagram_business_manage_messages"
)


@dataclass
class InstagramOAuthResult:
    access_token: str
    user_id: str
    username: str
    name: str
    expires_in: int | None
    permissions: list[str]


def _instagram_app_id() -> str:
    return (getattr(settings, "INSTAGRAM_APP_ID", "") or settings.META_APP_ID or "").strip()


def _instagram_app_secret() -> str:
    return (getattr(settings, "INSTAGRAM_APP_SECRET", "") or settings.META_APP_SECRET or "").strip()


def get_oauth_redirect_uri() -> str:
    configured = (getattr(settings, "INSTAGRAM_REDIRECT_URI", "") or "").strip()
    if configured:
        return configured if configured.endswith("/") else configured + "/"
    base = (getattr(settings, "PUBLIC_BASE_URL", "") or "http://127.0.0.1:8000").rstrip("/")
    return f"{base}/auth/instagram/callback/"


def build_authorize_url(*, state: str) -> str:
    client_id = _instagram_app_id()
    if not client_id:
        raise RuntimeError("INSTAGRAM_APP_ID missing in .env (Instagram product panel — not Facebook App ID)")
    scopes = (getattr(settings, "INSTAGRAM_OAUTH_SCOPES", "") or DEFAULT_SCOPES).strip()
    params = {
        "client_id": client_id,
        "redirect_uri": get_oauth_redirect_uri(),
        "scope": scopes,
        "response_type": "code",
        "state": state,
    }
    # Instagram Login authorize endpoint (requires Instagram App ID, not Facebook App ID)
    return f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"


def exchange_code_for_token(code: str) -> dict[str, Any]:
    """Exchange authorization code for short-lived Instagram user token."""
    # Meta sometimes appends #_ to the code
    code = (code or "").replace("#_", "").strip()
    resp = requests.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id": _instagram_app_id(),
            "client_secret": _instagram_app_secret(),
            "grant_type": "authorization_code",
            "redirect_uri": get_oauth_redirect_uri(),
            "code": code,
        },
        timeout=30,
    )
    data = resp.json() if resp.content else {}
    if resp.status_code >= 400 or "access_token" not in data:
        logger.error("IG code exchange failed: %s %s", resp.status_code, data)
        raise RuntimeError(data.get("error_message") or data.get("error") or str(data))
    return data


def exchange_long_lived_token(short_token: str) -> dict[str, Any]:
    resp = requests.get(
        "https://graph.instagram.com/access_token",
        params={
            "grant_type": "ig_exchange_token",
            "client_secret": _instagram_app_secret(),
            "access_token": short_token,
        },
        timeout=30,
    )
    data = resp.json() if resp.content else {}
    if resp.status_code >= 400 or "access_token" not in data:
        logger.warning("Long-lived exchange failed, using short-lived: %s", data)
        return {"access_token": short_token, "expires_in": 3600}
    return data


def fetch_instagram_profile(access_token: str, user_id: str | None = None) -> dict[str, Any]:
    fields = "user_id,username,name,account_type,profile_picture_url"
    # Prefer /me on graph.instagram.com
    resp = requests.get(
        "https://graph.instagram.com/v21.0/me",
        params={"fields": fields, "access_token": access_token},
        timeout=30,
    )
    if resp.ok:
        return resp.json()
    if user_id:
        resp2 = requests.get(
            f"https://graph.instagram.com/v21.0/{user_id}",
            params={"fields": fields, "access_token": access_token},
            timeout=30,
        )
        if resp2.ok:
            return resp2.json()
        raise RuntimeError(resp2.text)
    raise RuntimeError(resp.text)


def subscribe_instagram_webhooks(access_token: str, ig_user_id: str | None = None) -> dict[str, Any]:
    """
    Required so Meta POSTs incoming DMs to /webhooks/instagram/.
    POST /{ig-user-id|me}/subscribed_apps?subscribed_fields=messages,...
    """
    version = getattr(settings, "INSTAGRAM_GRAPH_VERSION", "v21.0")
    target = ig_user_id or "me"
    fields = (
        "messages,message_reactions,messaging_postbacks,messaging_seen,messaging_referral"
    )
    url = f"https://graph.instagram.com/{version}/{target}/subscribed_apps"
    resp = requests.post(
        url,
        params={"subscribed_fields": fields, "access_token": access_token},
        timeout=30,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text, "status": resp.status_code}
    if resp.status_code >= 400:
        logger.error("Webhook subscribe failed: %s", data)
    else:
        logger.info("Webhook subscribe ok: %s", data)
    return data


def complete_oauth(code: str) -> InstagramOAuthResult:
    short = exchange_code_for_token(code)
    short_token = short["access_token"]
    user_id = str(short.get("user_id") or "")
    permissions = short.get("permissions") or []
    if isinstance(permissions, str):
        permissions = [p.strip() for p in permissions.split(",") if p.strip()]

    long_data = exchange_long_lived_token(short_token)
    access_token = long_data["access_token"]
    expires_in = long_data.get("expires_in")

    profile = fetch_instagram_profile(access_token, user_id or None)
    ig_id = str(profile.get("user_id") or profile.get("id") or user_id)
    username = (profile.get("username") or f"user_{ig_id[-6:]}").lstrip("@")
    name = profile.get("name") or username

    return InstagramOAuthResult(
        access_token=access_token,
        user_id=ig_id,
        username=username,
        name=name,
        expires_in=int(expires_in) if expires_in else None,
        permissions=list(permissions),
    )


def upsert_business_from_oauth(result: InstagramOAuthResult) -> tuple[Business, Channel, bool]:
    """
    Create or update Business + Instagram Channel from OAuth result.
    Returns (business, channel, created_business).
    """
    channel = (
        Channel.objects.filter(type=ChannelType.INSTAGRAM, external_id=result.user_id)
        .select_related("business")
        .first()
    )
    created_business = False

    if channel:
        business = channel.business
    else:
        slug = slugify(result.username) or f"ig-{result.user_id[-8:]}"
        slug = re.sub(r"[^a-z0-9\-]", "", slug.lower())[:40] or f"ig-{result.user_id[-8:]}"
        if Business.objects.filter(pk=slug).exists():
            slug = f"{slug}-{result.user_id[-4:]}"
        business = Business.objects.create(
            id=slug,
            name=result.name or result.username,
            type=BusinessType.OTHER,
            description=f"Instagram @{result.username} vasitəsilə qoşulub.",
        )
        created_business = True

    channel, _ = Channel.objects.update_or_create(
        business=business,
        type=ChannelType.INSTAGRAM,
        defaults={
            "status": ChannelStatus.LIVE,
            "handle": f"@{result.username}",
            "external_id": result.user_id,
            "access_token": result.access_token,
            "last_error": "",
            "token_expires_at": (
                timezone.now() + timedelta(seconds=result.expires_in)
                if result.expires_in
                else None
            ),
        },
    )

    for ctype, status in (
        (ChannelType.WHATSAPP, ChannelStatus.COMING_SOON),
        (ChannelType.WEBSITE, ChannelStatus.COMING_SOON),
    ):
        Channel.objects.get_or_create(
            business=business,
            type=ctype,
            defaults={"status": status},
        )

    AISettings.objects.get_or_create(
        business=business,
        defaults={
            "assistant_name": "AI Assistant",
            "language": "az",
            "tone": "friendly",
            "business_type": business.type,
            "rules": (
                "Müştəri suallarını Knowledge Base-ə əsasən cavabla. "
                "Lead üçün ad soyad və +994 telefonu tələb et."
            ),
        },
    )

    desired_name = result.name or result.username
    if desired_name and business.name != desired_name:
        business.name = desired_name
        business.save(update_fields=["name"])

    # Ensure Meta sends DMs for this account to our webhook
    try:
        sub = subscribe_instagram_webhooks(result.access_token, result.user_id)
        if not sub.get("success") and sub.get("error"):
            channel.last_error = str(sub.get("error"))[:500]
            channel.save(update_fields=["last_error", "updated_at"])
    except Exception as exc:
        logger.exception("subscribe webhooks failed")
        channel.last_error = f"webhook subscribe: {exc}"[:500]
        channel.save(update_fields=["last_error", "updated_at"])

    return business, channel, created_business


def new_oauth_state() -> str:
    return secrets.token_urlsafe(24)

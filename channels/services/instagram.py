"""
Instagram Messaging via Meta Graph API (multi-tenant).

Credentials come from Channel rows created by Instagram OAuth.
Optional .env INSTAGRAM_* is only a fallback for single-tenant ops.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class InstagramCredentials:
    access_token: str
    ig_account_id: str
    api_host: str
    graph_version: str
    app_secret: str
    verify_token: str
    business_id: str | None = None


def _env_fallback_credentials() -> InstagramCredentials | None:
    token = (getattr(settings, "INSTAGRAM_ACCESS_TOKEN", "") or "").strip()
    ig_id = (getattr(settings, "INSTAGRAM_ACCOUNT_ID", "") or "").strip()
    if not token or not ig_id:
        return None
    host = (getattr(settings, "INSTAGRAM_API_HOST", "graph.instagram.com") or "graph.instagram.com").strip()
    return InstagramCredentials(
        access_token=token,
        ig_account_id=ig_id,
        api_host=host.replace("https://", "").rstrip("/"),
        graph_version=getattr(settings, "INSTAGRAM_GRAPH_VERSION", "v21.0"),
        app_secret=(getattr(settings, "META_APP_SECRET", "") or "").strip(),
        verify_token=(getattr(settings, "META_VERIFY_TOKEN", "aikomekci_verify") or "").strip(),
        business_id=(getattr(settings, "INSTAGRAM_BUSINESS_ID", "") or None),
    )


def credentials_from_channel(channel) -> InstagramCredentials | None:
    if not channel or not channel.access_token or not channel.external_id:
        return None
    host = (getattr(settings, "INSTAGRAM_API_HOST", "graph.instagram.com") or "graph.instagram.com").strip()
    # OAuth Instagram Login tokens use graph.instagram.com
    if getattr(settings, "INSTAGRAM_FORCE_GRAPH_HOST", True):
        host = "graph.instagram.com"
    return InstagramCredentials(
        access_token=channel.access_token,
        ig_account_id=channel.external_id,
        api_host=host.replace("https://", "").rstrip("/"),
        graph_version=getattr(settings, "INSTAGRAM_GRAPH_VERSION", "v21.0"),
        app_secret=(getattr(settings, "META_APP_SECRET", "") or "").strip(),
        verify_token=(getattr(settings, "META_VERIFY_TOKEN", "aikomekci_verify") or "").strip(),
        business_id=channel.business_id,
    )


def get_credentials_for_ig_account(ig_account_id: str) -> InstagramCredentials | None:
    from channels.models import Channel, ChannelType

    channel = (
        Channel.objects.filter(type=ChannelType.INSTAGRAM, external_id=str(ig_account_id))
        .select_related("business")
        .first()
    )
    creds = credentials_from_channel(channel)
    if creds:
        return creds
    fallback = _env_fallback_credentials()
    if fallback and fallback.ig_account_id == str(ig_account_id):
        return fallback
    return None


def get_credentials_for_business(business_id: str) -> InstagramCredentials | None:
    from channels.models import Channel, ChannelType

    channel = (
        Channel.objects.filter(business_id=business_id, type=ChannelType.INSTAGRAM)
        .exclude(access_token="")
        .first()
    )
    return credentials_from_channel(channel) or _env_fallback_credentials()


def get_instagram_credentials() -> InstagramCredentials | None:
    """Any live Instagram channel, else env fallback."""
    from channels.models import Channel, ChannelStatus, ChannelType

    channel = (
        Channel.objects.filter(type=ChannelType.INSTAGRAM, status=ChannelStatus.LIVE)
        .exclude(access_token="")
        .exclude(external_id="")
        .first()
    )
    return credentials_from_channel(channel) or _env_fallback_credentials()


def is_instagram_live() -> bool:
    from channels.models import Channel, ChannelStatus, ChannelType

    if Channel.objects.filter(
        type=ChannelType.INSTAGRAM, status=ChannelStatus.LIVE
    ).exclude(access_token="").exists():
        return True
    return _env_fallback_credentials() is not None


def verify_webhook_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Verify X-Hub-Signature-256. Instagram API apps sign with INSTAGRAM_APP_SECRET."""
    secrets: list[str] = []
    for key in ("INSTAGRAM_APP_SECRET", "META_APP_SECRET"):
        value = (getattr(settings, key, "") or "").strip()
        if value and value not in secrets:
            secrets.append(value)
    if not secrets:
        logger.warning("No app secret set; skipping Instagram signature check")
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    received = signature_header.removeprefix("sha256=")
    for app_secret in secrets:
        expected = hmac.new(
            app_secret.encode("utf-8"),
            msg=raw_body,
            digestmod=hashlib.sha256,
        ).hexdigest()
        if hmac.compare_digest(expected, received):
            return True
    return False


def send_instagram_text(
    *,
    recipient_igsid: str,
    text: str,
    credentials: InstagramCredentials | None = None,
) -> dict[str, Any]:
    creds = credentials or get_instagram_credentials()
    if not creds:
        raise RuntimeError("Instagram credentials not found for this account")

    text = (text or "").strip()
    if len(text) > 950:
        text = text[:947] + "..."

    payload = {
        "recipient": {"id": recipient_igsid},
        "message": {"text": text},
    }
    url = f"https://{creds.api_host}/{creds.graph_version}/{creds.ig_account_id}/messages"
    resp = requests.post(
        url,
        params={"access_token": creds.access_token},
        json=payload,
        timeout=30,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if resp.status_code >= 400:
        logger.error("Instagram send failed %s: %s", resp.status_code, data)
        url2 = f"https://{creds.api_host}/{creds.graph_version}/me/messages"
        resp2 = requests.post(
            url2,
            params={"access_token": creds.access_token},
            json=payload,
            timeout=30,
        )
        try:
            data2 = resp2.json()
        except Exception:
            data2 = {"raw": resp2.text}
        if resp2.status_code >= 400:
            raise RuntimeError(f"Instagram API error: {data2}")
        return data2
    return data


def fetch_ig_username(igsid: str, credentials: InstagramCredentials | None = None) -> str | None:
    creds = credentials or get_instagram_credentials()
    if not creds:
        return None
    try:
        url = f"https://{creds.api_host}/{creds.graph_version}/{igsid}"
        resp = requests.get(
            url,
            params={"fields": "username,name", "access_token": creds.access_token},
            timeout=15,
        )
        if resp.ok:
            data = resp.json()
            return data.get("username") or data.get("name")
    except Exception as exc:
        logger.debug("username lookup failed: %s", exc)
    return None

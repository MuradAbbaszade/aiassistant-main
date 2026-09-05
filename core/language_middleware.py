from __future__ import annotations

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from core.i18n import DEFAULT_LANG, normalize_lang


class LanguageMiddleware(MiddlewareMixin):
    """Resolve UI language from session (default: Azerbaijani)."""

    def process_request(self, request: HttpRequest):
        raw = request.session.get("ui_lang") or request.COOKIES.get("ui_lang") or DEFAULT_LANG
        lang = normalize_lang(raw)
        request.ui_lang = lang
        request.session["ui_lang"] = lang

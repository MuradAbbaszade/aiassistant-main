from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from core.i18n import SUPPORTED_LANGS, normalize_lang


@require_POST
def set_language(request):
    lang = normalize_lang(request.POST.get("language") or request.POST.get("lang"))
    if lang not in SUPPORTED_LANGS:
        lang = "az"
    request.session["ui_lang"] = lang
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    response = redirect(next_url)
    response.set_cookie("ui_lang", lang, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return response

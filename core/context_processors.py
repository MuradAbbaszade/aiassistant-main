from businesses.models import Business
from core.i18n import LANG_LABELS, SUPPORTED_LANGS, DEFAULT_LANG, normalize_lang, template_strings


def tenant(request):
    businesses = list(Business.objects.all())
    lang = normalize_lang(getattr(request, "ui_lang", None) or request.session.get("ui_lang") or DEFAULT_LANG)
    return {
        "current_business": getattr(request, "current_business", None),
        "all_businesses": businesses,
        "is_demo_logged_in": bool(request.session.get("demo_logged_in")),
        "demo_user_email": request.session.get("demo_user_email", "demo@aiassistant.local"),
        "demo_user_name": request.session.get("demo_user_name", "Demo Account"),
        "ui_lang": lang,
        "t": template_strings(lang),
        "lang_choices": [{"code": c, "label": LANG_LABELS[c]} for c in SUPPORTED_LANGS],
    }

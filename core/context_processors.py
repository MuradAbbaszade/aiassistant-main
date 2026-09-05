from businesses.models import Business
from core.i18n import LANG_LABELS, SUPPORTED_LANGS, DEFAULT_LANG, normalize_lang, template_strings


def tenant(request):
    businesses = list(Business.objects.all())
    lang = normalize_lang(getattr(request, "ui_lang", None) or request.session.get("ui_lang") or DEFAULT_LANG)
    logged_in = bool(
        (getattr(request, "user", None) and request.user.is_authenticated)
        or request.session.get("demo_logged_in")
    )
    name = request.session.get("demo_user_name")
    email = request.session.get("demo_user_email")
    if getattr(request, "user", None) and request.user.is_authenticated:
        name = request.user.get_full_name() or name or request.user.email
        email = request.user.email or email
    return {
        "current_business": getattr(request, "current_business", None),
        "all_businesses": businesses,
        "is_demo_logged_in": logged_in,
        "demo_user_email": email or "",
        "demo_user_name": name or "",
        "ui_lang": lang,
        "t": template_strings(lang),
        "lang_choices": [{"code": c, "label": LANG_LABELS[c]} for c in SUPPORTED_LANGS],
        "support_whatsapp_url": "https://wa.me/994705550117",
    }

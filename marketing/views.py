from django.shortcuts import render

from core.i18n import landing_payload


def landing(request):
    lang = getattr(request, "ui_lang", "az")
    ctx = landing_payload(lang)
    return render(request, "marketing/landing.html", ctx)

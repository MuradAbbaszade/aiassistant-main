from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ai.models import AISettings
from core.decorators import demo_login_required
from core.i18n import LANG_LABELS, localized_choice_pairs


@demo_login_required
@require_http_methods(["GET", "POST"])
def ai_settings_view(request):
    business = request.current_business
    settings_obj, _ = AISettings.objects.get_or_create(
        business=business,
        defaults={
            "assistant_name": "AI Assistant",
            "business_type": business.type,
        },
    )
    if request.method == "POST":
        settings_obj.assistant_name = request.POST.get("assistant_name", settings_obj.assistant_name)
        settings_obj.language = request.POST.get("language", settings_obj.language)
        settings_obj.tone = request.POST.get("tone", settings_obj.tone)
        settings_obj.response_length = request.POST.get(
            "response_length", settings_obj.response_length
        )
        settings_obj.rules = request.POST.get("rules", settings_obj.rules)
        settings_obj.business_type = business.type
        settings_obj.save()
        from core.i18n import get_translator

        tr = get_translator(getattr(request, "ui_lang", None))
        messages.success(request, tr.get("ai.save", "Saved") + " ✓")
        return redirect("ai:settings")

    lang = getattr(request, "ui_lang", None)
    language_choices = [(c.value, LANG_LABELS.get(c.value, c.label)) for c in AISettings.Language]
    tone_choices = localized_choice_pairs(lang, "ai.tone", [c.value for c in AISettings.Tone])
    length_choices = localized_choice_pairs(lang, "ai.len", [c.value for c in AISettings.ResponseLength])

    return render(
        request,
        "dashboard/ai_settings.html",
        {
            "ai_settings": settings_obj,
            "language_choices": language_choices,
            "tone_choices": tone_choices,
            "length_choices": length_choices,
            "active_nav": "ai_settings",
        },
    )

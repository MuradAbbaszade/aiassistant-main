from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.decorators import demo_login_required
from core.i18n import localized_choice_pairs
from knowledge.models import KnowledgeItem, KnowledgeType


@demo_login_required
def knowledge_list(request):
    business = request.current_business
    lang = getattr(request, "ui_lang", None)
    items = KnowledgeItem.objects.filter(business=business)
    by_type = {t.value: [] for t in KnowledgeType}
    for item in items:
        by_type.setdefault(item.type, []).append(item)
    type_choices = localized_choice_pairs(lang, "kb.type", [t.value for t in KnowledgeType])
    label_by_type = dict(type_choices)
    by_type_labeled = [(label_by_type.get(k, k), v) for k, v in by_type.items()]
    return render(
        request,
        "dashboard/knowledge.html",
        {
            "by_type_labeled": by_type_labeled,
            "type_choices": type_choices,
            "active_nav": "knowledge",
        },
    )


@demo_login_required
@require_http_methods(["POST"])
def knowledge_create(request):
    business = request.current_business
    keywords_raw = request.POST.get("keywords", "")
    keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
    KnowledgeItem.objects.create(
        business=business,
        type=request.POST.get("type") or KnowledgeType.FAQ,
        title=request.POST.get("title", "").strip() or "Başlıqsız",
        content=request.POST.get("content", "").strip(),
        keywords=keywords,
    )
    messages.success(request, "Knowledge item əlavə olundu — AI dərhal istifadə edə bilər.")
    return redirect("knowledge:list")


@demo_login_required
@require_http_methods(["POST"])
def knowledge_update(request, pk: int):
    item = get_object_or_404(KnowledgeItem, pk=pk, business=request.current_business)
    item.type = request.POST.get("type") or item.type
    item.title = request.POST.get("title", item.title).strip()
    item.content = request.POST.get("content", item.content).strip()
    keywords_raw = request.POST.get("keywords", "")
    item.keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
    item.save()
    messages.success(request, "Yeniləndi.")
    return redirect("knowledge:list")


@demo_login_required
@require_http_methods(["POST"])
def knowledge_delete(request, pk: int):
    item = get_object_or_404(KnowledgeItem, pk=pk, business=request.current_business)
    item.delete()
    messages.success(request, "Silindi.")
    return redirect("knowledge:list")

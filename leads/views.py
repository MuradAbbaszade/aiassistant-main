from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.decorators import demo_login_required
from core.i18n import localized_choice_pairs
from leads.models import Lead, LeadStatus


@demo_login_required
def lead_list(request):
    business = request.current_business
    leads = Lead.objects.filter(business=business)
    status_choices = localized_choice_pairs(
        getattr(request, "ui_lang", None),
        "leads.status",
        [c.value for c in LeadStatus],
    )
    return render(
        request,
        "dashboard/leads.html",
        {
            "leads": leads,
            "status_choices": status_choices,
            "active_nav": "leads",
        },
    )


@demo_login_required
@require_http_methods(["POST"])
def lead_update_status(request, pk: int):
    lead = get_object_or_404(Lead, pk=pk, business=request.current_business)
    status = request.POST.get("status")
    if status in {c.value for c in LeadStatus}:
        lead.status = status
        lead.save(update_fields=["status", "updated_at"])
        messages.success(request, "Status yeniləndi.")
    return redirect("leads:list")

import json

from django.shortcuts import redirect, render

from businesses.models import Business
from core.decorators import demo_login_required


@demo_login_required
def demo_chat(request):
    business = request.current_business
    if not business:
        return redirect("accounts:instagram_login")
    return render(
        request,
        "demo/chat.html",
        {
            "businesses": Business.objects.all(),
            "business": business,
            "scenario": [],
            "scenario_json": json.dumps([]),
            "active_nav": "demo",
        },
    )


def pick_business(request):
    """Legacy demo picker removed — go to Instagram login."""
    return redirect("accounts:instagram_login")

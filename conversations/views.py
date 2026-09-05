from django.shortcuts import get_object_or_404, render

from conversations.queries import customer_conversations
from core.decorators import demo_login_required


@demo_login_required
def conversation_list(request):
    business = request.current_business
    conversations = customer_conversations(business).prefetch_related("messages")
    selected_id = request.GET.get("c")
    selected = None
    if selected_id:
        selected = conversations.filter(pk=selected_id).first()
        if selected is None:
            # Don't open a filtered-out demo thread via ?c=
            selected = None
    elif conversations:
        selected = conversations[0]
    return render(
        request,
        "dashboard/conversations.html",
        {
            "conversations": conversations,
            "selected": selected,
            "active_nav": "conversations",
        },
    )

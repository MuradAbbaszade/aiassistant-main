from django.shortcuts import get_object_or_404, render

from conversations.models import Conversation
from core.decorators import demo_login_required


@demo_login_required
def conversation_list(request):
    business = request.current_business
    conversations = Conversation.objects.filter(business=business).prefetch_related("messages")
    selected_id = request.GET.get("c")
    selected = None
    if selected_id:
        selected = get_object_or_404(Conversation, pk=selected_id, business=business)
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

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from core import api
from core.views_i18n import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),
    path("", include("marketing.urls")),    path("", include("accounts.urls")),
    path("", include("analytics.urls")),
    path("", include("knowledge.urls")),
    path("", include("conversations.urls")),
    path("", include("leads.urls")),
    path("", include("channels.urls")),
    path("", include("ai.urls")),
    path("", include("demo.urls")),
    # API
    path("api/demo/chat/", api.demo_chat, name="api_demo_chat"),
    path("api/business/switch/", api.switch_business, name="api_business_switch"),
    path("api/knowledge/", api.knowledge_api, name="api_knowledge"),
    path("api/knowledge/<int:pk>/", api.knowledge_detail_api, name="api_knowledge_detail"),
    path("api/conversations/", api.conversations_api, name="api_conversations"),
    path("api/leads/<int:pk>/", api.lead_status_api, name="api_lead_status"),
    path("api/channels/instagram/connect/", api.instagram_connect_api, name="api_ig_connect"),
    path("api/analytics/", api.analytics_api, name="api_analytics"),
    # Instagram webhook also registered via channels.urls → /webhooks/instagram/
    # Future: path("webhooks/whatsapp/", ...),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

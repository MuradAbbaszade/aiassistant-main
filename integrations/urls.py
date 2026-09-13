from django.urls import path

from integrations import views

app_name = "integrations"

urlpatterns = [
    path("dashboard/integrations/", views.integrations_home, name="home"),
    path("dashboard/integrations/endpoints/create/", views.endpoint_create, name="endpoint_create"),
    path(
        "dashboard/integrations/endpoints/<int:pk>/toggle/",
        views.endpoint_toggle,
        name="endpoint_toggle",
    ),
    path(
        "dashboard/integrations/endpoints/<int:pk>/delete/",
        views.endpoint_delete,
        name="endpoint_delete",
    ),
    path(
        "dashboard/integrations/endpoints/<int:pk>/test/",
        views.endpoint_test,
        name="endpoint_test",
    ),
    path(
        "dashboard/integrations/deliveries/<int:pk>/retry/",
        views.delivery_retry,
        name="delivery_retry",
    ),
]

from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("onboarding/", views.onboarding_view, name="onboarding"),
    path("auth/instagram/", views.instagram_login_start, name="instagram_login"),
    path("auth/instagram/callback/", views.instagram_callback, name="instagram_callback"),
]

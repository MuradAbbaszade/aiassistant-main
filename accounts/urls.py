from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify-email/", views.verify_email_view, name="verify_email"),
    path("verify-email/resend/", views.resend_otp_view, name="resend_otp"),
    path("onboarding/", views.onboarding_view, name="onboarding"),
    path("onboarding/manual/", views.onboarding_manual, name="onboarding_manual"),
    path("onboarding/message-us/", views.onboarding_message_us, name="onboarding_message"),
    path("auth/instagram/", views.instagram_login_start, name="instagram_login"),
    path("auth/instagram/callback/", views.instagram_callback, name="instagram_callback"),
]

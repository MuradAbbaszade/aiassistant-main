from django.urls import path

from demo import views

app_name = "demo"

urlpatterns = [
    path("demo/", views.demo_chat, name="chat"),
    path("demo/pick/", views.pick_business, name="pick"),
]

from django.urls import path
from .views import (
    AboutAPIView,
    TeamAPIView,
    SupportAPIView,
)

app_name = "about"

urlpatterns = [
    path("", AboutAPIView.as_view()),
    path("team", TeamAPIView.as_view()),
    path("support", SupportAPIView.as_view()),
]

from django.urls import path
from .views import (
    ContactSubjectListAPIView,
    ContactSettingAPIView,
    ContactUsCreateAPIView,
)

app_name = "contact"

urlpatterns = [
    path("subjects", ContactSubjectListAPIView.as_view()),
    path("", ContactSettingAPIView.as_view()),
    path("contact", ContactUsCreateAPIView.as_view()),
]

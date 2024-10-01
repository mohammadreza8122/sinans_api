from django.urls import path
from .views import (
    SocialMediaListAPIView,
    SiteSettingRetrieveAPIView,
    ApplicationUrlAPIView,
    DDay,
)

app_name = "setting"

urlpatterns = [
    path("socials", SocialMediaListAPIView.as_view()),
    path("setting", SiteSettingRetrieveAPIView.as_view()),
    path("app-link", ApplicationUrlAPIView.as_view()),
    path("dday/", DDay.as_view()),
]

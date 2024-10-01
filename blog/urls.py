from django.urls import path
from .views import (
    ArticleListAPIView,
    VideoListAPIView,
    ArticleRetrieveAPIView,
    VideoRetrieveAPIView,
    BlogCommentAPIView,
)

app_name = "blog"

urlpatterns = [
    path("articles", ArticleListAPIView.as_view()),
    path("articles/<slug>", ArticleRetrieveAPIView.as_view()),
    path("videos", VideoListAPIView.as_view()),
    path("videos/<slug>", VideoRetrieveAPIView.as_view()),
    path("comment", BlogCommentAPIView.as_view()),
]

from rest_framework.generics import ListAPIView, RetrieveAPIView,ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils.encoding import uri_to_iri
from rest_framework import status
from .pagination import CustomLimitPagination
from rest_framework.response import Response
from .serializers import (
    Article,
    ArticleSerializer,
    Video,
    VideoSerializer,
    BlogCommentSerializer,
    BlogComment,
)


class ArticleListAPIView(ListAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    pagination_class = CustomLimitPagination


class ArticleRetrieveAPIView(RetrieveAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Article, slug=uri_to_iri(kwargs.get("slug")))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class VideoListAPIView(ListAPIView):
    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    pagination_class = CustomLimitPagination


class VideoRetrieveAPIView(RetrieveAPIView):
    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Video, slug=uri_to_iri(kwargs.get("slug")))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class BlogCommentAPIView(ListCreateAPIView):
    serializer_class = BlogCommentSerializer
    queryset = BlogComment.objects.filter(is_published=True)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "video",
        "article",
    ]

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer,user=user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer,user):
        serializer.save(user=user)
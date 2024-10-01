from rest_framework import serializers
from .models import Article, Video, BlogComment
from user.serializers import UserSerializer


class ArticleSerializer(serializers.ModelSerializer):


    class Meta:
        model = Article
        fields = "__all__"


class VideoSerializer(serializers.ModelSerializer):


    class Meta:
        model = Video
        fields = "__all__"


class BlogCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    class Meta:
        model = BlogComment
        exclude = ("is_published",)
        read_only_fields = ("user",)

from django.contrib import admin
from .models import Article, Video, BlogComment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    pass


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "is_published",
                    "user",
                    "article",
                    "video",
                    "text",
                    "score",
                )
            },
        ),
    )
    readonly_fields = ("score",)
    list_filter = ("article",)

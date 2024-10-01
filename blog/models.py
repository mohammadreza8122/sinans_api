from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models.signals import pre_save
from utilities.utils import unique_slug_generator
from user.models import User


class Video(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=120)
    text = RichTextUploadingField(verbose_name="توضیحات")
    meta_keywords = models.TextField(verbose_name="Meta Keywords", null=True)
    meta_description = models.TextField(verbose_name="Meta Description", null=True)
    date_created = models.DateTimeField(
        verbose_name="تاریخ انتشار",
        blank=True,
        null=True,
        auto_now_add=True,
    )
    slug = models.SlugField(
        verbose_name="فیلد URL",
        max_length=100,
        allow_unicode=True,
        blank=True,
        null=True,
        unique=True,
    )
    image = models.ImageField(
        verbose_name="عکس", upload_to="blog", blank=True, null=True
    )
    banner = models.ImageField(
        verbose_name="بنر", upload_to="blog", blank=True, null=True
    )
    video = models.FileField(verbose_name="ویدیو", upload_to="blog")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "ویدیو"
        verbose_name_plural = "ویدیو ها"


class Article(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=120)
    text = RichTextUploadingField(verbose_name="مقاله")
    meta_keywords = models.TextField(verbose_name="Meta Keywords", null=True)
    meta_description = models.TextField(verbose_name="Meta Description", null=True)
    date_created = models.DateTimeField(
        verbose_name="تاریخ انتشار",
        blank=True,
        null=True,
        auto_now_add=True,
    )
    slug = models.SlugField(
        verbose_name="فیلد URL",
        max_length=100,
        allow_unicode=True,
        blank=True,
        null=True,
        unique=True,
    )
    image = models.ImageField(
        verbose_name="عکس", upload_to="blog", blank=True, null=True
    )
    banner = models.ImageField(
        verbose_name="بنر", upload_to="blog", blank=True, null=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقاله ها"


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(pre_save_receiver, sender=Article)
pre_save.connect(pre_save_receiver, sender=Video)


class BlogComment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=True, blank=True, verbose_name="مقاله"
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, null=True, blank=True, verbose_name="ویدیو"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="کاربر"
    )
    text = models.TextField(verbose_name="بازخورد")
    score = models.PositiveSmallIntegerField(verbose_name="امتیاز")
    is_published = models.BooleanField(verbose_name="انتشار یابد؟", default=False)

    def __str__(self) -> str:
        return self.user.__str__()

    class Meta:
        verbose_name = "نظرات"
        verbose_name_plural = "نظرات"

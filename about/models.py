from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Team(models.Model):
    name = models.CharField(verbose_name="نام", max_length=255)
    title = models.CharField(verbose_name="عنوان/سمت", max_length=255)
    image = models.ImageField(verbose_name="تصویر", null=True, blank=True)
    email = models.EmailField(verbose_name="ایمیل", null=True, blank=True)
    instagram = models.CharField(
        verbose_name="اینستاگرام", max_length=255, null=True, blank=True
    )
    phone = models.CharField(
        verbose_name="شماره تماس", max_length=255, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.name} {self.title}"

    class Meta:
        verbose_name = "تیم"
        verbose_name_plural = "تیم"


class Support(models.Model):
    name = models.CharField(verbose_name="نام", max_length=255)
    title = models.CharField(verbose_name="عنوان/سمت", max_length=255)
    image = models.ImageField(verbose_name="تصویر", null=True, blank=True)
    email = models.EmailField(verbose_name="ایمیل", null=True, blank=True)
    instagram = models.CharField(
        verbose_name="اینستاگرام", max_length=255, null=True, blank=True
    )
    whatsapp = models.CharField(
        verbose_name="واتساپ", max_length=255, null=True, blank=True
    )
    phone = models.CharField(
        verbose_name="شماره تماس", max_length=255, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.name} {self.title}"

    class Meta:
        verbose_name = "پشتیبانی"
        verbose_name_plural = "پشتیبانی"


class About(models.Model):
    title = models.CharField(verbose_name="عنوان/سمت", max_length=255)
    text = models.TextField(verbose_name="توضیحات تکمیلی", null=True, blank=True)

    def __str__(self) -> str:
        return "درباره سینانس"

    class Meta:
        verbose_name = "درباره"
        verbose_name_plural = "درباره سینانس"


class AboutSection(models.Model):
    about = models.ForeignKey(
        About,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="درباره",
        related_name="sections",
    )
    title = models.CharField(verbose_name="عنوان", max_length=255)
    text = RichTextUploadingField(verbose_name="متن")
    image = models.ImageField(verbose_name="تصویر", null=True, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "بخش"
        verbose_name_plural = "بخش"


class Statistic(models.Model):
    about = models.ForeignKey(
        About,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="درباره",
        related_name="statistics",
    )
    row = models.PositiveIntegerField(verbose_name="ترتیب", default=1)
    title = models.CharField(verbose_name="عنوان", max_length=255)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "آمار"
        verbose_name_plural = "آمارها"
        ordering = ("row",)

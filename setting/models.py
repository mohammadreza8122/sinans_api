from django.db import models


class SiteSettings(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=255)
    site_url = models.URLField(verbose_name="آدرس سایت", null=True)
    android_url = models.CharField(
        verbose_name="آدرس دانلود اپ اندروید", null=True, blank=True , max_length=700
    )
    iphone_url = models.URLField(
        verbose_name="آدرس دانلود اپ آیفون", null=True, blank=True
    )
    logo = models.ImageField(verbose_name="لوگو", null=True)
    logo_mobile = models.ImageField(verbose_name="لوگو موبایل", null=True)
    fav_icon = models.ImageField(verbose_name="fav_icon", null=True)
    meta_keywords = models.TextField(verbose_name="Meta Keywords", null=True)
    meta_description = models.TextField(verbose_name="Meta Description", null=True)
    address = models.TextField(verbose_name="آدرس")
    number = models.TextField(verbose_name="شماره تماس")
    text_1 = models.TextField(verbose_name="متن اول صفحه اصلی", null=True, blank=True)
    text_2 = models.TextField(verbose_name="متن دوم صفحه اصلی", null=True, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "تنظیمات"
        verbose_name_plural = "تنظیمات"


class Banner(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=255)
    image = models.ImageField(verbose_name="تصویر")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "بنر"
        verbose_name_plural = "بنرها"


class ImportantLinks(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=255)
    link = models.CharField(verbose_name="لینک", max_length=500)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "لینک"
        verbose_name_plural = "لینک های مفید"


class SocialMedia(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=255)
    link = models.URLField(verbose_name="لینک")
    image = models.ImageField(verbose_name="تصویر")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "شبکه اجتماعی"
        verbose_name_plural = "شبکه های اجتماعی"


class FAQ(models.Model):
    question = models.TextField(verbose_name="سوال")
    answer = models.TextField(verbose_name="پاسخ")

    def __str__(self) -> str:
        return self.question

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات متداول"


class SiteSwitch(models.Model):
    is_enabled = models.BooleanField(default=True)

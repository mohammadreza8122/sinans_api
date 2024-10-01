from django.db import models
from location_field.models.plain import PlainLocationField
from user.models import User

class ContactSetting(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=255)
    number = models.CharField(verbose_name="شماره تماس", max_length=255)
    instagram = models.CharField(verbose_name="اینستاگرام", max_length=255)
    email = models.CharField(verbose_name="ایمیل", max_length=255)
    address = models.CharField(verbose_name="آدرس", max_length=255)
    location = PlainLocationField(
        based_fields=["city"], zoom=7, blank=True, null=True, verbose_name="نقشه"
    )

    def __str__(self) -> str:
        return "تنظیمات تماس باما"

    class Meta:
        verbose_name = "تنظیمات تماس باما"
        verbose_name_plural = "تنظیمات تماس باما"


class ContactSubject(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=255)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "موضوع"
        verbose_name_plural = "موضوعات"


class ContactUs(models.Model):
    is_checked = models.BooleanField(verbose_name="بررسی شده؟",default=False)
    title = models.CharField(verbose_name="عنوان", max_length=255)
    date_created = models.DateTimeField(verbose_name="زمان ایجاد", auto_now=True)
    subject = models.ForeignKey(
        ContactSubject, on_delete=models.SET_NULL, null=True, verbose_name="موضوع"
    )
    number = models.CharField(verbose_name="شماره", max_length=255)
    text = models.TextField(verbose_name="متن")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "فرم تماس باما"
        verbose_name_plural = "فرم های تماس باما"

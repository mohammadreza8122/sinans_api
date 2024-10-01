from django.db import models
from utilities.utils import unique_slug_generator
from django.db.models.signals import pre_save
from ckeditor_uploader.fields import RichTextUploadingField


class Province(models.Model):
    title = models.CharField(verbose_name="نام استان", unique=True, max_length=255)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "استان"
        verbose_name_plural = "استانها"
        ordering = ("title",)


class City(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="استان",
        related_name="cities",
    )
    title = models.CharField(verbose_name="نام شهر", unique=True, max_length=255)
    on_home = models.BooleanField(
        verbose_name="شهر پربازدید؟",
        default=False,
        help_text="8 شهر پربازدید در صفحه اسلی و برای دسترسی سریع کاربر نمایش داده میشوند",
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"
        ordering = ("title",)


class HomeCareCategory(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=255)
    slug = models.SlugField(
        verbose_name="اسلاگ",
        help_text="اگر خالی باشد به صورت خودکار از عنوان استفاده میکند",
        unique=True,
        allow_unicode=True,
        null=True,
        blank=True,
    )
    father = models.ForeignKey(
        "HomeCareCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="دسته پدر",
        related_name="category_children",
    )
    image = models.ImageField(
        verbose_name="عکس", blank=True, null=True, upload_to="category"
    )
    meta_description = models.CharField(
        verbose_name="تگ توضیحات",
        help_text="Meta Description Tag For Seo",
        max_length=500,
        null=True,
        blank=True,
    )
    meta_keywords = models.CharField(
        verbose_name="تگ کلمات کلیدی",
        help_text="Meta Keywords Tag For Seo",
        max_length=500,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        if self.father:
            return f"{self.title} زیر دسته {self.father.title}"
        else:
           return self.title

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندیها"
        ordering = ("title",)


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class HomeCareService(models.Model):
    is_active = models.BooleanField(verbose_name="فعال?", default=True)
    is_deleted = models.BooleanField(verbose_name="حذف شده", default=False)
    title = models.CharField(verbose_name="عنوان", max_length=255)
    category = models.ForeignKey(
        HomeCareCategory, on_delete=models.SET_NULL, verbose_name="دسته بندی", null=True
    )
    image = models.ImageField(verbose_name="تصویر", null=True, blank=True)
    banner = models.ImageField(verbose_name="بنر", null=True, blank=True)
    icon = models.ImageField(verbose_name="آیکون", null=True, blank=True)
    text = RichTextUploadingField(verbose_name="توضیحات", null=True, blank=True)

    objects = ServiceManager()

    def __str__(self):
        return self.title

    def delete(self):
        self.is_deleted = True
        self.save()

    class Meta:
        verbose_name = "خدمت در منزل"
        verbose_name_plural = "خدمات در منزل"
        ordering = ("title", "category")


class ServiceExtraInfo(models.Model):
    service = models.ForeignKey(
        HomeCareService,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="خدمات",
        related_name="infos",
    )
    text = models.TextField(verbose_name="نکته")

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        verbose_name = "نکته"
        verbose_name_plural = "نکات تکمیلی"


class ServiceFAQ(models.Model):
    service = models.ForeignKey(
        HomeCareService,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="خدمات",
        related_name="faqs",
    )
    title = models.CharField(verbose_name="سوال", max_length=255)
    text = models.TextField(verbose_name="جواب")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات متداول"


class HomeCareServicePrice(models.Model):
    service = models.ForeignKey(
        HomeCareService, on_delete=models.SET_NULL, verbose_name="خدمت", null=True
    )
    city = models.ForeignKey(City, models.SET_NULL, null=True, verbose_name="شهر")
    company = models.ForeignKey(
        "user.HomeCareCompany",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="شرکت",
    )
    price = models.PositiveBigIntegerField(verbose_name="قیمت", default=0)

    def __str__(self) -> str:
        if self.service and self.city:
            return f"{self.service} و {self.city} و {self.price}"
        else:
            return "خدمات یا شهر انتخاب نشده"

    class Meta:
        verbose_name = "قیمت"
        verbose_name_plural = "قیمت خدمات"


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(pre_save_receiver, sender=HomeCareCategory)

from django.db import models
from treebeard.mp_tree import MP_Node

class Category(MP_Node):
    title = models.CharField(verbose_name="عنوان", max_length=255)
    slug = models.SlugField(
        verbose_name="اسلاگ",
        help_text="اگر خالی باشد به صورت خودکار از عنوان استفاده میکند",
        unique=True,
        allow_unicode=True,
        null=True,
        blank=True,
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
    cites = models.JSONField(null=True, blank=True)
    company_list = models.JSONField(null=True, blank=True)

    node_order_by = ['path',]

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندیها"
        ordering = ("title",)


    def __str__(self) -> str:
        if self.get_parent():
            return f"{self.title} زیر دسته {self.get_parent().title}"
        else:
           return self.title







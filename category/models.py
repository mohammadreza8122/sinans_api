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

    node_order_by = ['path',]

    def __str__(self) -> str:
        if self.get_parent():
            return f"{self.title} زیر دسته {self.get_parent().title}"
        else:
           return self.title







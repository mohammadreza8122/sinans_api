from django.contrib import admin
from category.models import Category
from treebeard.admin import TreeAdmin
from category.forms import CategoryAdminForm


@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    search_fields = ("title",)
    form = CategoryAdminForm
    readonly_fields = ('company_list', 'cites')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if '_position' in form.base_fields:
            del form.base_fields['_position']
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj._position = 'sorted-child'
        super().save_model(request, obj, form, change)


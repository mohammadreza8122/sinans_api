from django.contrib import admin
from category.models import Category
from treebeard.admin import TreeAdmin
from category.forms import CategoryAdminForm
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType


from django.contrib.admin import SimpleListFilter

class ParentFilter(SimpleListFilter):
    title = 'parent'
    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        parents = set(Category.get_tree())
        return [(p.id, str(p)) for p in parents]

    def queryset(self, request, queryset):
        if self.value():
            cat = Category.objects.get(id=self.value())
            return cat.get_children()
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_filter = [ParentFilter, ]
    search_fields = ("title", "slug")
    list_display = ('title', 'get_father', 'created_by')
    form = CategoryAdminForm
    readonly_fields = ('created_by', )
    fieldsets = (
        ('Detail info', {
            'fields': (
                'title', 'slug', 'image',
                'meta_description', 'meta_keywords',
                '_ref_node_id', 'created_by'
            )
        }),
    )
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if '_position' in form.base_fields:
            del form.base_fields['_position']
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj._position = 'sorted-child'
        super().save_model(request, obj, form, change)


    def get_father(self, instance):
        if instance.get_parent():
            return instance.get_parent()
        return ''
    get_father.short_description = "دسته پدر"


    def created_by(self, instance):
        log = LogEntry.objects.filter(object_id=instance.id,
                                       content_type_id = ContentType.objects.get_for_model(instance).pk,
                                       action_flag     = ADDITION).first()
        if not log:
            return ''

        if log.user.first_name and log.user.last_name:
            create_by = format_html('<a  href="/admin/user/user/{}/change/">{} {}</a>'.format(
                log.user.pk, log.user.first_name, log.user.last_name
            ))

        else:
            create_by = format_html('<a href="/admin/user/user/{}/change/">{}</a>'.format(
                log.user.pk, log.user.number,
            ))
        return create_by
    created_by.short_description = "ایحاد شده توسط"






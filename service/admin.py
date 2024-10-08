from venv import create

from django.contrib import admin
from .models import (
    HomeCareService,
    HomeCareCategory,
    HomeCareServicePrice,
    City,
    Province,
    ServiceFAQ,
    ServiceExtraInfo,
)
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType



class CityInline(admin.TabularInline):
    model = City
    extra = 1


class ServiceFAQInline(admin.StackedInline):
    model = ServiceFAQ
    extra = 1


class ServiceExtraInfoInline(admin.StackedInline):
    model = ServiceExtraInfo
    extra = 1


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    inlines = (CityInline,)
    list_filter = ("title",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("title", "province")
    list_filter = ("title", "province")


@admin.register(HomeCareService)
class HomeCareServiceAdmin(admin.ModelAdmin):
    readonly_fields = ['created_by',]

    list_display = ("title", "category", "is_active", "is_deleted", 'created_by')
    search_fields = ("title",)
    list_filter = ("category__title", )
    actions = ("delete_services",)
    raw_id_fields = ('category',)
    inlines = [ServiceFAQInline, ServiceExtraInfoInline]

    @admin.action(description="حذف")
    def delete_services(self, request, queryset):
        for obj in queryset:
            obj.is_deleted = True
            obj.save()

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions


    def created_by(self, instance):
        log = LogEntry.objects.filter(object_id=instance.id,
                                       content_type_id = ContentType.objects.get_for_model(instance).pk,
                                       action_flag     = ADDITION).first()

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


    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',
            'autocomplete/service.js',)
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css',
            )
        }



@admin.register(HomeCareCategory)
class HomeCareCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "father", "created_by")
    search_fields = ("title",)
    raw_id_fields = ('father',)
    readonly_fields = ("created_by", )

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',
            'autocomplete/category.js',)
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css',
                'search_bar.css'
            )
        }

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


    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',
            'autocomplete/service.js',)
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css',
            )
        }


@admin.register(HomeCareServicePrice)
class HomeCareServicePriceAdmin(admin.ModelAdmin):
    list_display = ("service", "city", "company", "price_display")
    list_filter = ("service", "city","company")


    def price_display(self, obj):
        return format_html("<span>{}</span>", f"{obj.price:,.0f}")

    price_display.short_description = "قیمت"


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
from django.utils.numberformat import format
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

    list_display = ("title", "category", "is_active", "is_deleted")
    search_fields = ("title", "category")
    # list_filter = ("title", "category")
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
        create_by = format_html('<a class="btn btn-info" href="/admin/user/user/{}/change/">{} {}</a>'.format(
            log.user.pk, log.user.first_name, log.user.last_name
        ))
        return create_by
    created_by.short_description = "ایحاد شده توسط"



@admin.register(HomeCareCategory)
class HomeCareCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "father")
    search_fields = ("title", "father")
    raw_id_fields = ('father',)


@admin.register(HomeCareServicePrice)
class HomeCareServicePriceAdmin(admin.ModelAdmin):
    list_display = ("service", "city", "price_display")
    list_filter = ("service", "city","company")


    def price_display(self, obj):
        return format_html("<span>{}</span>", f"{obj.price:,.0f}")

    price_display.short_description = "قیمت"


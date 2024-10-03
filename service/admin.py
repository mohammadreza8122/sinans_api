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
from ajax_select import register, LookupChannel
from ajax_select import make_ajax_form


@register('categories')
class CategoryLookup(LookupChannel):
    model = HomeCareCategory

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)[:50]  # لیمیت برای بهبود عملکرد
    def format_item_display(self, item):
        return u"<span class='tag'>{}</span>".format(item.name)


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
    form = make_ajax_form(HomeCareCategory, {'category': 'categories'})
    list_display = ("title", "category", "is_active", "is_deleted")
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


@admin.register(HomeCareCategory)
class HomeCareCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "father")
    # list_filter = ("title", "father")
    raw_id_fields = ('father',)


@admin.register(HomeCareServicePrice)
class HomeCareServicePriceAdmin(admin.ModelAdmin):
    list_display = ("service", "city", "price_display")
    list_filter = ("service", "city","company")


    def price_display(self, obj):
        return format_html("<span>{}</span>", f"{obj.price:,.0f}")

    price_display.short_description = "قیمت"


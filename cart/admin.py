from django.contrib import admin
import jdatetime
from .models import Cart, CartItem, HomeCareOrder,OrderItem
import csv
from django.http import HttpResponse
from django.contrib.admin.filters import SimpleListFilter
from django.utils.timezone import localtime
import jdatetime
import jdatetime
from django.utils.formats import time_format
import pytz
from datetime import timedelta
from rangefilter.filters import (
    DateRangeFilterBuilder,
    DateTimeRangeFilterBuilder,
    NumericRangeFilterBuilder,
    DateRangeQuickSelectListFilterBuilder,
)
from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin
from jdatetime import datetime as jdatetime
from datetime import datetime as gregorian_datetime
import jdatetime


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['quantity', 'service']
    readonly_fields = ['service', ]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = (CartItemInline,)
    list_display = ("__str__", "is_ordered")
    # list_filter = ("user",)

def generate_invoice_excel(modeladmin, request, queryset):

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="invoices.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "نام و نام خانوادگی",
            "نام شرکت",
            "تاریخ و ساعت",
            "شهر",
            "کد پیگیری",
            "هزینه نهایی",
            "خدمات",
        ]
    )

    total_cost = 0
    for order in queryset:
        user_name = (
            order.user.username
            if order.user.username
            else order.user.number or order.user.username
        )
        company = ", ".join(
            [item.company.title for item in order.orderitem_set.all()]
        )
        due_date_time = (
            jdatetime.datetime.fromgregorian(datetime=order.date_created).strftime(
                "%Y/%m/%d %H:%M:%S"
            )
            if order.date_created
            else ""
        )
        city_name = order.city.title if order.city else ""
        pay_token = order.pay_token if order.pay_token else ""
        final_price = order.final_price

        services = ", ".join(
            [item.service.service.title for item in order.orderitem_set.all()]
        )

        writer.writerow(
            [
                user_name,
                company,
                due_date_time,
                city_name,
                pay_token,
                final_price,
                services,
            ]
        )
        total_cost += final_price

    writer.writerow(
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    writer.writerow(["جمع صورتحساب:", f"{total_cost:,}"])

    return response


def export_as_csv(modeladmin, request, queryset):
   
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)

    model = queryset.model
    fields = [field.verbose_name for field in model._meta.fields]

    writer.writerow(fields)

    for obj in queryset:
        row = []
        for field in model._meta.fields:
            if field.name == "status":
                status_value = getattr(obj, field.name)
                for status in obj.ORDER_STATUS:
                    if status[0] == status_value:
                        row.append(status[1])
                        break
            elif field.name == "cart_in_place":
                cart_in_place_value = getattr(obj, field.name)
                for cart_place in obj.CART_PLACE:
                    if cart_place[0] == cart_in_place_value:
                        row.append(cart_place[1])
                        break
            elif field.name in ["is_paid", "is_done"]:
                value = getattr(obj, field.name)
                row.append("بله" if value else "خیر")
            elif field.name == "date_created":
                date_created = getattr(obj, field.name)
                jalali_date = jdatetime.datetime.fromgregorian(
                    datetime=date_created
                ).strftime("%Y/%m/%d")
                time_12_hour = time_format(date_created, "P")
                row.append(f"{time_12_hour} - {jalali_date}")
            else:
                value = getattr(obj, field.name)
                row.append(value if value is not None else "وارد نشده")
        writer.writerow(row)

    return response

class HomeCareOrderInline(admin.StackedInline):
    model = OrderItem
    readonly_fields = ("service",)
    extra = 1

    
@admin.register(HomeCareOrder)
class HomeCareOrderAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    inlines = [HomeCareOrderInline]

    actions = [export_as_csv, generate_invoice_excel]
    list_display = (
        "__str__",
        "get_price",
        "get_register_code",
        "pay_token",
        "jalali",
        "status",
        "is_paid",
        "is_done",
    )
    # list_filter = (
    #     "user",
    #     "status",
    #     "ordered_companies",
    #     "date_created"
    # )
    search_fields = ("pay_token",)
    list_filter = (
        "user",
        "status",
        "ordered_companies",
        "date_created",
        (
            "date_created",
            DateRangeFilterBuilder(
                title="بازه دلخواه",
            ),
        ),
    )
    #
    class DateCreatedFilter(SimpleListFilter):
        title = "تاریخ ثبت درخواست"
        parameter_name = "date_created_filter"

        def lookups(self, request, model_admin):
            return (
                ("today", "امروز"),
                ("this_week", "این هفته"),
                ("this_month", "این ماه"),
                ("custom", "بازه دلخواه"),
            )

        def queryset(self, request, queryset):
            if self.value() == "today":
                return queryset.filter(
                    date_created__date=localtime(
                        request.GET.get("date_created_filter", None)
                    ).date()
                )
            elif self.value() == "this_week":
                return queryset.filter(
                    date_created__week=localtime(
                        request.GET.get("date_created_filter", None)
                    )
                    .isocalendar()
                    .week
                )
            elif self.value() == "this_month":
                return queryset.filter(
                    date_created__month=localtime(
                        request.GET.get("date_created_filter", None)
                    ).month
                )
            elif self.value() == "custom":
                start_date = request.GET.get("date_created_filter__gte", None)
                end_date = request.GET.get("date_created_filter__lt", None)
                if start_date and end_date:
                    return queryset.filter(
                        date_created__gte=start_date, date_created__lt=end_date
                    )
            return queryset
    
    def get_register_code(self, obj):
        return obj.user.register_code

    def get_price(self, obj):
        return f"{obj.final_price:,} تومان"

    def jalali(self, obj):
        date_created = obj.date_created

        date_created_tehran = date_created.astimezone(pytz.timezone('Asia/Tehran'))

        jalali_date = jdatetime.datetime.fromgregorian(datetime=date_created_tehran)

        return f"{jalali_date.strftime('%H:%M')} - {jalali_date.strftime('%Y/%m/%d')}"

    jalali.short_description = "تاریخ"
    get_register_code.short_description = "معرف"
    get_price.short_description = "هزینه کل"
    export_as_csv.short_description = "خروجی اکسل"
    generate_invoice_excel.short_description = "صورتحساب"
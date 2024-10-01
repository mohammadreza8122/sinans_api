from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
import jdatetime
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
import qrcode
from io import BytesIO
from .models import (
    User,
    RegisterCode,
    CityManager,
    UserAddress,
    CompanyManager,
    HomeCareCompany,
    UserBenefit,
    UserMessage,
    Complaint,
)
from django.contrib.humanize.templatetags.humanize import intcomma
from setting.models import SiteSettings
from django.contrib import messages
import csv
from django.http import HttpResponse
from django.http import HttpResponse
import jdatetime
import jdatetime
from datetime import timedelta
from django.contrib.humanize.templatetags.humanize import intcomma
from io import BytesIO
from django.contrib import messages
import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.contrib import admin
import csv
from django.http import HttpResponse
from django.contrib.admin.filters import SimpleListFilter
from django.utils.timezone import localtime
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
from datetime import timedelta
from jdatetime import datetime as jdatetime
from datetime import datetime as gregorian_datetime
import jdatetime


@admin.register(RegisterCode)
class RegisterCodeAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyManager)
class CompanyManagerAdmin(admin.ModelAdmin):
    list_display = ("user", "company")
    list_filter = ("user", "company")


@admin.register(HomeCareCompany)
class HomeCareCompanyAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "city", "pay_later", "is_plus")
    list_filter = ("user", "city", "is_plus")
    filter_horizontal = ("allowed_categories",)


@admin.register(CityManager)
class CityManagerAdmin(admin.ModelAdmin):
    list_display = ("user", "get_cities", "order_access")
    list_filter = ("user", "city")
    filter_horizontal = ("city", "allowed_categories")

    def get_cities(self, obj):
        return [f"{c}" for c in obj.city.all()]

    # def get_services(self, obj):
    #     return [f"{c}" for c in obj.services.all()]

    get_cities.short_description = "شهر ها"
    # get_services.short_description = "خدمات"


admin.site.unregister(Group)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
        field_classes = None


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "__str__",
        "first_name",
        "last_name",
        "is_staff",
        "jalali",
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "head_admin",
                    "invite_code",
                    "first_name",
                    "last_name",
                    "sex",
                    "number",
                    "image",
                    "otp",
                    "otp_created",
                    "email",
                    "zip_code",
                    "province",
                    "city",
                    "national_code",
                    "national_card_image",
                    "register_code",
                    "qrcode",
                    "company",
                    "first_company",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    readonly_fields = ("register_code",)
    ordering = ("-date_joined",)
    actions = ("generate_qr_code",)
    form = CustomUserChangeForm

    def jalali(self, obj):
        t = jdatetime.date.fromgregorian(
            day=obj.date_joined.day,
            month=obj.date_joined.month,
            year=obj.date_joined.year,
        )
        return t

    jalali.short_description = "تاریخ عضویت"

    @admin.action(description="ایجاد QRCODE")
    def generate_qr_code(self, request, queryset):
        site_setting = SiteSettings.objects.last()
        link = f"{site_setting.site_url}/login?code="
        for obj in queryset:
            if not obj.invite_code:
                messages.error(request=request, message="کد دعوت برای کاربر تعریف نشده")
                return
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"{link}{obj.invite_code.code}")
            qr.make(fit=True)

            # Create an image QR code
            img = qr.make_image(fill_color="black", back_color="white")

            # Save the image to a buffer
            buffer = BytesIO()
            img.save(buffer)
            buffer.seek(0)

            # Save the image to the qr_code field of the model instance
            obj.qrcode.save("qr_code.png", buffer, save=True)

        messages.error(request=request, message="QRCODE با موفقیت ایجاد شد")


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    pass


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_checked", "date_created")
    list_filter = ("user", "date_created")


def export_as_csv(modeladmin, request, queryset):
    """
    Admin action to export selected rows as a CSV file.
    """
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)

    if start_date and end_date:
        queryset = queryset.filter(
            date_create__gte=start_date, date_create__lte=end_date
        )
    elif start_date:
        queryset = queryset.filter(date_create__gte=start_date)
    elif end_date:
        queryset = queryset.filter(date_create__lte=end_date)
    elif request.GET.get("today", None):
        today = timezone.now().date()
        queryset = queryset.filter(date_create__date=today)
    elif request.GET.get("last_7_days", None):
        last_7_days = timezone.now().date() - timedelta(days=7)
        queryset = queryset.filter(date_create__gte=last_7_days)
    elif request.GET.get("last_month", None):
        last_month = timezone.now().date() - relativedelta(months=1)
        queryset = queryset.filter(date_create__gte=last_month)
    elif request.GET.get("last_year", None):
        last_year = timezone.now().date() - relativedelta(years=1)
        queryset = queryset.filter(date_create__gte=last_year)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)

    model = queryset.model
    fields = [
        "نام و نام خانوادگی",
        "کد پیگیری سفارش",
        "خدمات",
        "تسویه شده",
        "مبلغ (تومان)",
    ]

    writer.writerow(fields)

    for obj in queryset:
        if obj.user.first_name and obj.user.last_name:
            user_name = f"{obj.user.first_name} {obj.user.last_name}"
        elif obj.user.number:
            user_name = obj.user.number
        elif obj.user.username:
            user_name = obj.user.useranme
        else:
            user_name = "کاربر بدون نام"

        if obj.order and obj.order.cart and obj.order.cart.items.all():
            for cart_item in obj.order.cart.items.all():
                row = [
                    user_name,
                    obj.order.pay_token,
                    cart_item.service.service.title if cart_item.service else "-",
                    _("بله") if obj.paid else _("خیر"),
                    f"{intcomma(int(obj.price))} تومان",
                ]
                writer.writerow(row)
        else:
            row = [
                user_name,
                obj.order.pay_token if obj.order else "-",
                "-",
                _("بله") if obj.paid else _("خیر"),
                f"{intcomma(int(obj.price))} تومان",
            ]
            writer.writerow(row)

    return response

@admin.register(UserBenefit)
class UserBenefitAdmin(admin.ModelAdmin):
    list_display = ("user", "paid", "price")
    list_filter = (
        "user",
        "paid",
        "date_created",
        (
            "date_created",
            DateRangeFilterBuilder(
                title="بازه دلخواه",
            ),
        ),
    )
    
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
            
            
    
    actions = [export_as_csv]
    export_as_csv.short_description = "خروجی اکسل"
    
    

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("issue", "email_phone", "seen")
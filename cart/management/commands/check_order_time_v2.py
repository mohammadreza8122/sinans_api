from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from cart.management.commands.check_order_time_notif import chain_allowed_categories
from cart.models import OrderItem
from user.models import UserMessage, CompanyManager, CityManager
from django.utils import timezone
from django.utils.timezone import localtime
from sms_ir import SmsIr
from time import strftime, gmtime
from service.models import HomeCareCategory


def get_all_child_categories(category):
    child_categories = HomeCareCategory.objects.filter(father=category)
    all_child_categories = list(child_categories)
    for child_category in child_categories:
        all_child_categories.extend(get_all_child_categories(child_category))
    return all_child_categories


def send_sms(to, order_code, date, pattern_code=325648):
    sms_ir = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023",
    )
    response = sms_ir.send_verify_code(
        to,
        pattern_code,
        [
            {"name": "PAYTOKEN", "value": order_code},
            {"name": "DATETIME", "value": date},
        ],
    )
    return response


class Command(BaseCommand):
    help = "Checks orders and creates UserMessage objects if necessary"

    def handle(self, *args, **options):
        orders = OrderItem.objects.filter(is_done=False, status="ongoing")

        for order in orders:
            if order.order.due_date_time:
                now = timezone.localtime(timezone.now())
                local_order_time = localtime(order.order.due_date_time)
                time_delta_order = timedelta(hours=local_order_time.hour, minutes=local_order_time.minute, seconds=local_order_time.second)
                time_delta_now = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
                time_since_due = time_delta_order - time_delta_now

                user = order.order.user
                company = order.company
                georgian_date = localtime(order.order.due_date_time) - now
                today = timezone.now().day

                if order.order.date_created.day != today and order.order.due_date_time.day == today:
                    if (3 * 60 + 50) < time_since_due.total_seconds() // 60 < (4 * 60 + 10) and not order.sms_send_company_admin:
                        managers = CompanyManager.objects.filter(company=company)
                        for manager in managers:
                            UserMessage.objects.create(
                                user=manager.user,
                                title="خدمات پیش رو",
                                text=f"سفارش با کد {order.order.pay_token} در کمتر از {strftime('%H:%M:%S', gmtime(georgian_date.total_seconds()))} به موعد انجام می‌رسد",
                            )
                            send_sms(
                                manager.user.number,
                                order.order.pay_token,
                                strftime("%H:%M:%S", gmtime(georgian_date.total_seconds())),
                            )
                        order.sms_send_company_admin = True
                        order.save()

                    if 3 * 60 + 50 < time_since_due.total_seconds() // 60 < 4 * 60 + 10 and order.status == "ongoing" and not order.sms_send_admin_for_onmission:
                        city_managers = CityManager.objects.filter(city=user.city)
                        order.sms_send_admin_for_onmission = True
                        order.save()
                        for manager in city_managers:
                            if manager.allowed_categories.exists():
                                categories = chain_allowed_categories(manager.allowed_categories.all())
                                if categories and order.service.service.category in categories:
                                    UserMessage.objects.create(
                                        user=manager.user,
                                        title="پیگیری اعزام نیرو",
                                        text=f"وضعیت سفارش با کد {order.order.pay_token} که کمتر از {strftime('%H:%M:%S', gmtime(time_since_due.total_seconds()))} هنوز تغییر نکرده",
                                    )
                                    send_sms(
                                        manager.user.number,
                                        order.order.pay_token,
                                        strftime("%H:%M:%S", gmtime(georgian_date.total_seconds())),
                                        pattern_code=875864,  
                                    )

from user.models import UserMessage
from sms_ir import SmsIr
from time import strftime, gmtime
from django.utils.timezone import localtime

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

def notify_company_manager(manager, order, georgian_date):
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

def notify_city_manager(manager, order, time_since_due):
    UserMessage.objects.create(
        user=manager.user,
        title="پیگیری اعزام نیرو",
        text=f"وضعیت سفارش با کد {order.order.pay_token} که کمتر از {strftime('%H:%M:%S', gmtime(time_since_due.total_seconds()))} هنوز تغییر نکرده",
    )
    send_sms(
        manager.user.number,
        order.order.pay_token,
        strftime("%H:%M:%S", gmtime(time_since_due.total_seconds())),
        pattern_code=875864,  # الگوی متفاوت برای پیام به مدیر شهر
    )

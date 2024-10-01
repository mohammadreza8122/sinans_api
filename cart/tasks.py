from celery import shared_task
from django.utils.timezone import timedelta, now
from cart.serializers import AddItemSerializer
from user.models import UserMessage
from sms_ir import SmsIr
from time import strftime, gmtime
from django.utils.timezone import localtime
from datetime import timedelta
from django.utils import timezone
from .tasks import notify_company_managers_task, notify_city_managers_task


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


@shared_task
def notify_company_managers_task(order_id, manager_id):
    from cart.models import OrderItem
    from user.models import CompanyManager

    order = OrderItem.objects.get(id=order_id)
    manager = CompanyManager.objects.get(id=manager_id)

    georgian_date = localtime(order.order.due_date_time) - now()
    notify_company_manager(manager, order, georgian_date)


@shared_task
def notify_city_managers_task(order_id, manager_id):
    from cart.models import OrderItem
    from user.models import CityManager

    order = OrderItem.objects.get(id=order_id)
    manager = CityManager.objects.get(id=manager_id)

    time_since_due = order.order.due_date_time - now()
    notify_city_manager(manager, order, time_since_due)


def schedule_tasks(order):
    now = timezone.localtime(timezone.now())
    time_delta_order = order.order.due_date_time - now

    if time_delta_order < timedelta(hours=4):
        # مدیران شرکت
        managers = CompanyManager.objects.filter(company=order.company)
        for manager in managers:
            notify_company_managers_task.apply_async(
                (order.id, manager.id),
                # eta=now + time_delta_order - timedelta(hours=4)
            )

        # مدیران شهر
        city_managers = CityManager.objects.filter(city=order.order.user.city)
        for manager in city_managers:
            notify_city_managers_task.apply_async(
                (order.id, manager.id),
                # eta=now + time_delta_order - timedelta(hours=4)
            )





from datetime import timedelta
from cart.models import OrderItem
from user.models import CityManager, UserMessage
from django.utils import timezone
from service.views import chain_allowed_categories
from django.utils.timezone import localtime
from myproject.tasks import send_sms_task

def check_orders():
    orders = OrderItem.objects.filter(is_done=False, status="ongoing")

    for order in orders:
        try:
            now = timezone.localtime(timezone.now(), timezone.get_default_timezone())

            if order.order.due_date_time:
                if (order.order.date_created.day == order.order.due_date_time.day) and (
                    (now - localtime(order.order.date_created)) >= timedelta(minutes=7)
                    and (now - localtime(order.order.date_created)) < timedelta(minutes=13)
                ):
                    process_order(order)

        except Exception as e:
            print('Error:', e)
            continue


# تابع برای پردازش هر سفارش
def process_order(order):
    city_managers = CityManager.objects.filter(city=order.order.city)

    if not order.sms_send_city_managers:
        order.sms_send_city_managers = True
        order.save()

        for manager in city_managers:
            if manager.allowed_categories.exists():
                categories = chain_allowed_categories(manager.allowed_categories.all())

                if categories and order.service.service.category in categories:
                    send_notifications(order, manager)


# تابع برای ارسال پیامک و پیام به کاربر
def send_notifications(order, manager):
    text = f" وضعیت سفارش با کد {order.order.pay_token} در شهر {order.order.city} هنوز تغییر نکرده "
    UserMessage.objects.create(
        user=manager.user,
        title="پیگیری ارسال نیرو",
        text=text,
    )
    
    # ارسال پیامک با استفاده از Celery
    send_sms_task.delay(manager.user.number, order.order.pay_token, order.order.city.title)

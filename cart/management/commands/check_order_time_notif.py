from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from cart.models import HomeCareOrder, OrderItem
from service.models import HomeCareCategory
from user.models import CityManager, UserMessage, CompanyManager
from django.utils import timezone
import jdatetime
from time import strftime
from time import gmtime
from service.views import get_all_child_categories
from django.utils.timezone import localtime
from sms_ir import SmsIr

def chain_allowed_categories(allowed_categories):
    all_categories = list(allowed_categories)

    for category in allowed_categories:
        chain_category = None
        get_all = True
        while_count = 1
        if not category.father:
            for i in category.category_children.all():
                if i in allowed_categories:
                    get_all = False
            if get_all:
                all_categories.extend(get_all_child_categories(category))
        else:
            while while_count < HomeCareCategory.objects.count():
                while_count += 1
                if category in allowed_categories:
                    chain_category = category

                    for i in category.category_children.all():
                        if i in allowed_categories:
                            chain_category = category
                            while_count = 1000
                    if chain_category in allowed_categories:
                        break
            active_chain = True
            chain_two = False
            chain_three = False
            chain_four = False
            chain_five = False
            chain_six = False
            chain_seven = False
            if chain_category:

                for i in chain_category.category_children.all():
                    if i in allowed_categories:
                        active_chain = False
                if active_chain:
                    chain_two = chain_category.category_children.all()
                    all_categories.extend(chain_two)
            if chain_two:

                for x in chain_two:
                    all_categories.extend(x.category_children.all())
                    chain_three = x.category_children.all()
            if chain_three:
                for x in chain_three:
                    all_categories.extend(x.category_children.all())
                    chain_four = x.category_children.all()
            if chain_four:
                for x in chain_four:
                    all_categories.extend(x.category_children.all())
                    chain_five = x.category_children.all()
            if chain_five:
                for x in chain_five:
                    all_categories.extend(x.category_children.all())
                    chain_six = x.category_children.all()
            if chain_six:
                for x in chain_six:
                    all_categories.extend(x.category_children.all())
                    chain_seven = x.category_children.all()
            if chain_seven:
                for x in chain_seven:
                    all_categories.extend(x.category_children.all())
    return all_categories


def check_negative(s):
    try:
        f = float(s)
        if f < 0:
            return True
        # Otherwise return false
        return False
    except ValueError:
        return False


def send_msggg(to, order_code, city):

    sms_ir = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023",
    )
    response = sms_ir.send_verify_code(
        to,
        978882,
        [
            {"name": "PAYTOKEN", "value": order_code},
            {"name": "CITY", "value": city},
        ],
    )

    return response


class Command(BaseCommand):
    help = "Checks orders and creates UserMessage objects if necessary"

    def handle(self, *args, **options):
        # Get all orders
        orders = OrderItem.objects.filter(is_done=False, status="ongoing")

        # Iterate through the orders
        for order in orders:
            try:
                now = timezone.localtime(timezone.now(), timezone.get_default_timezone())
                if order.order.due_date_time:
                    if (order.order.date_created.day == order.order.due_date_time.day) and (
                        (now - localtime(order.order.date_created)) >= timedelta(minutes=7)
                        and (now - localtime(order.order.date_created)) < timedelta(minutes=13)
                    ):
                        georgian_date = localtime(order.order.due_date_time) - now
                        total_seconds = georgian_date.total_seconds()

                        remain_time = strftime("%H:%M:%S", gmtime(total_seconds))

                        text = f" وضعیت سفارش با کد {order.order.pay_token} در شهر {order.order.city} هنوز تغییر نکرده "

                        if not order.sms_send_city_managers:
                            city_managers = CityManager.objects.filter(city=order.order.city)
                            order.sms_send_city_managers = True
                            order.save()

                            for manager in city_managers:
                                if manager.allowed_categories.exists():

                                    categories = chain_allowed_categories(
                                        manager.allowed_categories.all()
                                    )

                                    if categories:

                                        if order.service.service.category in categories:
                                            UserMessage.objects.create(
                                                user=manager.user,
                                                title="پیگیری ارسال نیرو",
                                                text=text,
                                            )

                                            ss = send_msggg(
                                                manager.user.number,
                                                order.order.pay_token,
                                                order.order.city.title,
                                            )

            except:
                continue
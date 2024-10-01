from datetime import timedelta
from django.core.management.base import BaseCommand
from cart.models import HomeCareOrder, OrderItem
from service.models import HomeCareCategory
from user.models import CityManager, UserMessage
from django.utils import timezone
from sms_ir import SmsIr


def get_allowed_categories_with_children(allowed_categories):
    all_categories = list(allowed_categories)

    for category in allowed_categories:
        if not category.father:
            has_child_in_allowed = any(child in allowed_categories for child in category.category_children.all())
            if not has_child_in_allowed:
                all_categories.extend(category.get_all_child_categories())
        else:
            current_category = category
            while current_category and current_category not in allowed_categories:
                current_category = current_category.father

            if current_category:
                child_categories = current_category.category_children.all()
                all_categories.extend(child_categories)

                for child in child_categories:
                    all_categories.extend(child.get_all_child_categories())
    return all_categories


def is_negative(value):
    try:
        return float(value) < 0
    except ValueError:
        return False


def send_sms(to, order_code, city):
    sms_service = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023",
    )
    response = sms_service.send_verify_code(
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
        orders = OrderItem.objects.filter(is_done=False, status="ongoing")

        for order_item in orders:
            try:
                now = timezone.localtime()

                if order_item.order.due_date_time:
                    time_difference = now - timezone.localtime(order_item.order.date_created)
                    if time_difference >= timedelta(minutes=5) and time_difference < timedelta(minutes=15):

                        if not order_item.sms_send_city_managers:
                            city_managers = CityManager.objects.filter(city=order_item.order.city)
                            order_item.sms_send_city_managers = True
                            order_item.save()

                            text = f"وضعیت سفارش با کد {order_item.order.pay_token} در شهر {order_item.order.city} هنوز تغییر نکرده است."
                            
                            for manager in city_managers:
                                if manager.allowed_categories.exists():
                                    categories = get_allowed_categories_with_children(manager.allowed_categories.all())

                                    if order_item.service.service.category in categories:
                                        UserMessage.objects.create(
                                            user=manager.user,
                                            title="پیگیری ارسال نیرو",
                                            text=text,
                                        )

                                        send_sms(manager.user.number, order_item.order.pay_token, order_item.order.city.title)

            except Exception as e:
                self.stderr.write(f"Error processing order {order_item.id}: {str(e)}")
                continue

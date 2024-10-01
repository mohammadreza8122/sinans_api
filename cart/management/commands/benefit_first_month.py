from django.core.management.base import BaseCommand
from user.models import UserBenefit, UserMessage,User
import jdatetime


class Command(BaseCommand):
    # Cron job per day 
    def handle(self, *args, **options):
        benefits = UserBenefit.objects.filter(paid=False)
        get_head_admin = User.objects.filter(head_admin=True).first()
        if int(jdatetime.date.today().day) == 1 and get_head_admin:
            text = "سود تصویه نشده با کد پیکگیری {} و کاربر {}"
            for i in benefits:

                pay_token = i.order.pay_token if i.order else "بدون کد پیگیری"
                user = i.user.username if i.user else "بدون کاربر"

                if i.order.is_paid and i.order.is_done:
                    obj = UserMessage.objects.create(user=get_head_admin,title="سود تصویه نشده",text=text.format(pay_token,user))
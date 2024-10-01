from django.db import models
from user.models import User, UserAddress , HomeCareCompany
from service.models import HomeCareServicePrice, City
from django_jalali.db import models as jmodels


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    is_ordered = models.BooleanField(verbose_name="سفارش شده", default=False)

    def total_price(self):
        total = 0
        order_items = self.items.all()
        for item in order_items:
            total += item.service.price * item.quantity
        return total

    def __str__(self) -> str:
        if self.user and self.user.username:
            return self.user.username
        elif self.user and self.user.number:
            return self.user.number
        else:
            return str(self.id)

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبد خرید"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        verbose_name="سبدخرید",
        null=True,
        related_name="items",
    )
    service = models.ForeignKey(
        HomeCareServicePrice, on_delete=models.SET_NULL, null=True, verbose_name="خدمات"
    )
    quantity = models.PositiveIntegerField(verbose_name="تعداد", default=1)

    def __str__(self) -> str:
        if self.service and self.service.service:
            return self.service.service.title
        else:
            return str(self.id)

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم های سبد خرید"



class HomeCareOrder(models.Model):
    ORDER_STATUS = (
        ("ongoing", "خدمات پیش رو"),
        ("onmission", "اعزام نیرو"),
        ("previous", "خدمات گذشته"),
        ("canceled", "خدمات لغو شده"),
    )
    CART_PLACE = (
        ("online", "آنلاین"),
        ("place", "در محل"),
    )
    # editable = False
    sms_sent_head_admin = models.BooleanField(default=False,)
    sms_send_city_managers =  models.BooleanField(default=False)
    sms_send_company_admin = models.BooleanField(default=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    address = models.ForeignKey(
        UserAddress,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="آدرس",
    )
    cart = models.ForeignKey(
        Cart, on_delete=models.SET_NULL, null=True, verbose_name="سبد خرید"
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, verbose_name="شهر"
    )
    ordered_companies = models.ManyToManyField(HomeCareCompany,related_name="ordered_companies",null=True,verbose_name="کمپانی",help_text="کمپانی های که خدماتشان خریداری شده است در اینجا نمایش داده میشود")
    date_created = models.DateTimeField(
        verbose_name="تاریخ ایجاد", auto_now_add=True, null=True,editable=True
    )
    is_paid = models.BooleanField(verbose_name="پرداخت شده", default=False)
    is_done = models.BooleanField(verbose_name="انجام شده", default=False)
    

    status = models.CharField(
        verbose_name="وضعیت", max_length=255, choices=ORDER_STATUS
    )
    cart_in_place = models.CharField(
        verbose_name="نوع پرداخت", max_length=255, choices=CART_PLACE, null=True
    )
    final_price = models.PositiveIntegerField(
        verbose_name="هزینه نهایی پرداخت شده", default=0
    )
    pay_token = models.CharField(
        verbose_name="کد پیگیری", max_length=1000, null=True, blank=True, unique=True
    )
    text = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    due_date = models.CharField(
        verbose_name="تاریخ اعزام نیرو", max_length=255, null=True, blank=True
    )
    due_time = models.CharField(
        verbose_name="ساعت اعزام نیرو", max_length=255, null=True, blank=True
    )
    due_date_time = models.DateTimeField(
        verbose_name="ساعت و تاریخ اعزام نیرو", null=True, blank=True
    )
    invite_code = models.CharField(verbose_name='معرف',max_length=255,null=True,blank=True)
    def __str__(self) -> str:
        if self.user.number:
            return self.user.number
        elif self.user.username:
            return self.user.username
        else:
            return "کاربر بدون نام و شماره"

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"
        ordering = ("-date_created",)

        
class OrderItem(models.Model):
    ORDER_STATUS = (
        ("ongoing", "خدمات پیش رو"),
        ("onmission", "اعزام نیرو"),
        ("previous", "خدمات گذشته"),
        ("canceled", "خدمات لغو شده"),
    )
    sms_sent_head_admin = models.BooleanField(
        default=False,verbose_name='ارسال پیام برای ادمین کل',
    )
    sms_send_city_managers =  models.BooleanField(
        default=False,verbose_name='ارسال پیام برای مدیر شهری'
    )
    sms_send_company_admin = models.BooleanField(
        default=False,verbose_name='ارسال پیام برای ادمین شرکتی'
    )
    sms_send_admin_for_onmission = models.BooleanField(
        default=False,verbose_name='ارسال پیام به مدیر شهری برای پیگیری اعزام نیرو'
    )
    status = models.CharField(
        verbose_name="وضعیت", max_length=255, choices=ORDER_STATUS,default="ongoing"
    )
    company = models.ForeignKey(HomeCareCompany,on_delete=models.SET_NULL,null=True,verbose_name="شرکت")
    service = models.ForeignKey(
        HomeCareServicePrice, on_delete=models.SET_NULL,editable=False, null=True, verbose_name="خدمات"
    )
    quantity = models.PositiveIntegerField(verbose_name="تعداد", default=1)
    order = models.ForeignKey(HomeCareOrder,on_delete=models.CASCADE,null=True)

    is_done = models.BooleanField(verbose_name="انجام شده", default=False)

    def __str__(self):
        return str(self.id)
    class Meta:
        verbose_name = "آیتم های سفارش"
        verbose_name_plural = "آیتم های سفارش"

class OrderAddress(models.Model):
    order = models.ForeignKey(
        HomeCareOrder, on_delete=models.SET_NULL, verbose_name="سفارش", null=True ,db_constraint=True
    )
    name = models.CharField(verbose_name="نام بیمار", max_length=255)
    address = models.TextField(verbose_name="آدرس")
    zip_code = models.CharField(verbose_name="کدپستی", max_length=10)
    plak = models.CharField(verbose_name="پلاک", max_length=3)
    number_1 = models.CharField(verbose_name="شماره همراه", max_length=11)
    number_2 = models.CharField(verbose_name="شماره ثابت", max_length=11)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "اطلاعات آدرس سفارش"
        verbose_name_plural = "اطلاعات آدرس سفارش"
        
        

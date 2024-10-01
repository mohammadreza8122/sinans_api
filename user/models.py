from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import random
import string
from django.utils import timezone
from service.models import Province, City, HomeCareService, HomeCareCategory

def generate_random_char():
    characters = string.ascii_letters + string.digits
    random_chars = [random.choice(characters) for _ in range(12)]
    random_string = "".join(random_chars)
    return random_string


class RegisterCode(models.Model):
    code = models.CharField(
        verbose_name="کد دعوت", max_length=12, default=generate_random_char
    )

    def __str__(self) -> str:
        return self.code

    class Meta:
        verbose_name = "کد دعوت"
        verbose_name_plural = "کد دعوت"


class User(AbstractUser):
    SEX_TYPE = (
        ("male", "مرد"),
        ("female", "زن"),
    )
    head_admin = models.BooleanField(verbose_name="ادمین کل",default=False)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        null=True,
        blank=False,
    )
    first_name = models.CharField(
        verbose_name="نام", max_length=150, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name="نام خانوادگی", max_length=150, blank=True, null=True
    )
    sex = models.CharField(
        verbose_name="جنسیت", max_length=255, choices=SEX_TYPE, default="male"
    )
    number = models.CharField(
        verbose_name="شماره همراه", null=True, unique=
        True, max_length=11
    )
    image = models.ImageField(
        upload_to="user/profile", verbose_name="عکس", null=True, blank=True
    )
    otp = models.CharField(
        verbose_name="رمز یکبار مصرف",
        max_length=6,
        null=True,
        blank=True,
        default="112233",
    )
    otp_created = models.DateTimeField(
        verbose_name="زمان ایجاد otp", null=True, blank=True, default=timezone.now
    )
    email = models.EmailField(verbose_name="ایمیل", null=True, blank=True)
    zip_code = models.CharField(
        verbose_name="کد پستی", max_length=10, null=True, blank=True
    )
    province = models.ForeignKey(
        Province, on_delete=models.SET_NULL, null=True, verbose_name="استان"
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, verbose_name="شهر"
    )
    register_code = models.CharField(verbose_name="کد معرف", max_length=50)
    national_code = models.CharField(verbose_name="کد ملی", max_length=10)
    national_card_image = models.ImageField(
        verbose_name="تصویر کارت ملی", upload_to="user/profile", null=True, blank=True
    )
    invite_code = models.ForeignKey(
        RegisterCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="کد دعوت من",
    )
    
    qrcode = models.ImageField(
        verbose_name="QRCODE", upload_to="user/qrcode", null=True, blank=True
    )
    company = models.ForeignKey(
        "user.HomeCareCompany",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="شرکت",
        related_name="user_company",
    )
    first_company = models.ForeignKey(
        "user.HomeCareCompany",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="زیر مجموعه شرکت",
        related_name="user_first_company",
    )

    def __str__(self):
        if self.number:
            if self.first_name and self.last_name:
                return f"{self.number} - {self.first_name} - {self.last_name}"
            return f"{self.number}"
        elif self.username:
            return self.username
        else:
            return "کاربر بدون نام و شماره"

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ("-id",)


class   CityManager(models.Model):
    service_access = models.BooleanField(
        verbose_name="دسترسی به قیمت ها", default=False
    )
    order_access = models.BooleanField(verbose_name="دسترسی به تیکت ها", default=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="کاربر",
        related_name="manager",
    )
    city = models.ManyToManyField(City, verbose_name="شهر")
    allowed_categories = models.ManyToManyField(
        HomeCareCategory,
        verbose_name="دسته های خدمات قابل دسترسی",
        related_name="accessible_cities",
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.user.__str__()

    class Meta:
        verbose_name = "مدیر"
        verbose_name_plural = "مدیران شهری"


class HomeCareCompany(models.Model):
    is_plus = models.BooleanField(verbose_name="عضو سینانس پلاس",null=True,default=False)
    title = models.CharField(
        verbose_name="نام شرکت", max_length=255, null=True, blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="مدیر شرکت",
        related_name="company_owner",
    )
    allowed_categories = models.ManyToManyField(
        HomeCareCategory,
        verbose_name="دسته های خدمات قابل دسترسی",
        related_name="accessible_companies",
        blank=True,
        null=True
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, verbose_name="شهر"
    )
    pay_later = models.BooleanField(
        verbose_name="پرداخت در محل",
        default=False,
        help_text="با فعال کردن این گزینه مشتریان این شرکت می توانند پرداخت در محل داشته باشند",
    )

    def __str__(self) -> str:
        if self.title:
            return self.title
        return self.user.__str__()

    class Meta:
        verbose_name = "شرکت"
        verbose_name_plural = "شرکت ها"


class CompanyManager(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="ادمین شرکت",
        related_name="company_manager",
    )
    company = models.ForeignKey(
        HomeCareCompany, on_delete=models.SET_NULL, null=True, verbose_name="شرکت"
    )
    
    def __str__(self) -> str:
        return self.company.__str__()

    class Meta:
        verbose_name = "ادمین"
        verbose_name_plural = "ادمین شرکت ها"


class UserMessage(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="فرستنده",
        related_name="sender_messages",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="کاربر",
        related_name="user_messages",
    )
    title = models.CharField(verbose_name="موضوع", max_length=255, null=True)
    text = models.TextField(verbose_name="متن", null=True)
    is_checked = models.BooleanField(verbose_name="بررسی شده", default=False)
    date_created = models.DateTimeField(verbose_name="تاریخ ایجاد", auto_now_add=True)

    def __str__(self) -> str:
        return self.user.__str__()

    class Meta:
        verbose_name = "پیام"
        verbose_name_plural = "پیام های کاربر"


class UserBenefit(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="کاربر"
    )
    date_created = models.DateTimeField(verbose_name="تاریخ ایجاد",null=True,blank=True,auto_now_add=True)
    paid = models.BooleanField(verbose_name="تسویه شده", default=False)
    price = models.PositiveIntegerField(verbose_name="سود", default=0)
    order = models.ForeignKey(
        "cart.HomeCareOrder", on_delete=models.SET_NULL, null=True, verbose_name="سفارش"
    )


    def __str__(self) -> str:
        return self.user.__str__()

    class Meta:
        verbose_name = "سود کاربر"
        verbose_name_plural = "سودهای کاربر"


class UserAddress(models.Model):
    is_deleted = models.BooleanField(verbose_name="حذف شده ؟", default=False)
    title = models.CharField(verbose_name="عنوان", max_length=255, null=True)
    name = models.CharField(verbose_name="نام", max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    province = models.CharField(
        verbose_name="استان", max_length=60, blank=True, null=True
    )
    city = models.CharField(verbose_name="شهر", max_length=60)
    address = models.TextField(verbose_name="آدرس")
    zip_code = models.CharField(
        verbose_name="کد پستی", max_length=30, null=True, blank=True
    )
    number = models.CharField(
        verbose_name="شماره تماس", null=True, blank=True, max_length=30
    )

    def __str__(self):
        return f"{self.province} - {self.city} - {self.address} - {self.zip_code}"

    def delete(self):
        self.is_deleted = True
        self.save()

    class Meta:
        verbose_name = "آدرس کاربر"
        verbose_name_plural = "آدرس کاربر"
        
        
class Complaint(models.Model):
    seen = models.BooleanField(verbose_name='بررسی شده',null=True,default=False)
    issue = models.CharField(verbose_name='موضوع',null=True,max_length=255)
    email_phone = models.CharField(verbose_name='ایمیل / شماره تماس',null=True,max_length=100)
    text = models.TextField(verbose_name='متن',null=True)

    def __str__(self) -> str:
        if self.issue :
            return self.issue
        else:
            return "نامشخص"

    class Meta:
        verbose_name = "انتقاد و پیشنهاد و شکایت"
        verbose_name_plural = "انتقادات پیشنهادات شکایات"        
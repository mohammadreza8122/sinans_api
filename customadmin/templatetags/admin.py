from django.template import Library
from blog.models import Article,Video
from user.models import User,CityManager
from service.models import HomeCareService,HomeCareServicePrice
from cart.models import HomeCareOrder
from contact.models import ContactUs

register = Library()


@register.simple_tag
def service_count():
    return HomeCareService.objects.count()


@register.simple_tag
def order_count():
    return HomeCareOrder.objects.count()


@register.simple_tag
def user_count():
    return User.objects.count()


@register.simple_tag
def articles_count():
    return Article.objects.count()

@register.simple_tag
def video_count():
    return Video.objects.count()

@register.simple_tag
def manager_count():
    return CityManager.objects.count()

@register.simple_tag
def contactus_count():
    return ContactUs.objects.count()

@register.simple_tag
def price_count():
    return HomeCareServicePrice.objects.count()

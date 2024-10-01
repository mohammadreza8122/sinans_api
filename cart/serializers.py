from rest_framework import serializers

from service.models import HomeCareService, HomeCareServicePrice
from .models import Cart, CartItem, OrderAddress, HomeCareOrder, OrderItem
from service.serializers import HomeCareServicePriceSerializer
from user.serializers import UserAddressSerializer
from jdatetime import datetime as jdatetime
from user.serializers import HomeCareCompanySerializer
from datetime import datetime
from jalali_date import date2jalali, datetime2jalali
from jalali_date import date2jalali, datetime2jalali
from django.utils.timezone import localtime
from django.utils.formats import time_format
import pytz
from datetime import timedelta
from rest_framework import serializers
from .models import Cart, CartItem, OrderAddress, HomeCareOrder
from service.serializers import HomeCareServicePriceSerializer
from user.serializers import UserAddressSerializer
from jdatetime import date, datetime as jdatetime
from jdatetime import datetime as jdatetime
from user.serializers import HomeCareCompanySerializer
from datetime import datetime
from jalali_date import date2jalali, datetime2jalali
from django.utils.timezone import localtime
import jdatetime
from django.utils.formats import time_format
import pytz
from datetime import timedelta
from user.models import HomeCareCompany

class ShortServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeCareService
        fields = ("title","image")

class CompanyHomecareSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomeCareCompany
        fields = ("__all__")  


class ShortPriceHandlerSerializer(serializers.ModelSerializer):
    service = ShortServiceSerializer()
    company = CompanyHomecareSerializer()

    class Meta:
        model = HomeCareServicePrice
        fields = ("service", "company")


class OrderUpdateSerializer(serializers.ModelSerializer):

 
    class Meta:
        model = HomeCareOrder
        exclude = ("user","cart")
        read_only_fields = (
            "status",
            "date_created",
            "pay_token",
            "final_price",
            "is_paid",
            "is_done",
            "cart",
            "city",
            "due_date_time"
        )
class OrderSerializer(serializers.ModelSerializer):
    ordered_companies = serializers.SerializerMethodField()

    def get_ordered_companies(self, obj):
        companies = obj.ordered_companies.all()
        return HomeCareCompanySerializer(companies, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "address" in representation and representation["address"]:
            representation["address"] = UserAddressSerializer(instance.address).data
        if "cart" in representation and representation["cart"]:
            representation["cart"] = [
                CartItemSerializer(item).data for item in instance.cart.items.all()
            ]
        if "city" in representation and representation["city"]:
            representation["city"] = {
                "id": instance.city.id,
                "title": instance.city.title,
            }

        return representation
    # def update(self, instance, validated_data):
    #     due_date_validated = validated_data["due_date"].split("-")
    #     instance.due_time = validated_data["due_time"]
    #     instance.due_date = validated_data["due_date"]
    #     instance.address = validated_data["address"]

    #     # due_date = jdatetime.JalaliToGregorian(due_date_validated[0],due_date_validated[1],due_date_validated[2])
    #     due_date = jdatetime.date(year=int(due_date_validated[0]),month=int(due_date_validated[1]),day=int(due_date_validated[2]))

    #     converted_date = jdatetime.date.togregorian(due_date)
    #     instance.due_date_time_date= converted_date

    #     instance.due_date_time_time = validated_data["due_time"]
    #     instance.save()
    #     return instance

    class Meta:
        model = HomeCareOrder
        #exclude = ("user","cart")
        fields = '__all__'
        read_only_fields = (
            "status",
            "date_created",
            "pay_token",
            "final_price",
            "is_paid",
            "is_done",
            "cart",
            "city",
            "ordered_companies",
            "user",
        )




class OrderItemSerializer(serializers.ModelSerializer):
    service = ShortPriceHandlerSerializer()
    order = serializers.SerializerMethodField("get_order")
    def get_order(self,obj):
        return OrderSerializer(obj.order).data
    class Meta:
        model = OrderItem
        exclude = ("sms_send_city_managers","sms_sent_head_admin")






class ManagerOrderSerializer(serializers.ModelSerializer):
    due_date_time = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    def get_company(self, obj):
        company = obj.company
        serializer = HomeCareCompanySerializer(company)
        return serializer.data

    def get_due_date_time(self, obj):

        due_date_time = obj.due_date_time

        due_date_time_tehran = due_date_time.astimezone(pytz.timezone("Asia/Tehran"))

        jalali_date = jdatetime.datetime.fromgregorian(datetime=due_date_time_tehran)

        return f"{jalali_date.strftime('%H:%M')} - {jalali_date.strftime('%Y/%m/%d')}"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "address" in representation and representation["address"]:
            representation["address"] = UserAddressSerializer(instance.address).data
        if "cart" in representation and representation["cart"]:
            representation["cart"] = [
                CartItemSerializer(item).data for item in instance.cart.items.all()
            ]
        if "city" in representation and representation["city"]:
            representation["city"] = {
                "id": instance.city.id,
                "title": instance.city.title,
            }

        return representation

    class Meta:
        model = HomeCareOrder
        exclude = ("user",)
        read_only_fields = (
            "status",
            "date_created",
            "pay_token",
            "final_price",
            "is_paid",
            "is_done",
            "cart",
            "city",
        )

class CartItemSerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField()

    def get_service(self, obj):
        return HomeCareServicePriceSerializer(obj.service).data

    class Meta:
        model = CartItem
        fields = ("id", "service", "quantity")


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        return [CartItemSerializer(item).data for item in obj.items.all()]

    class Meta:
        model = Cart
        fields = "__all__"


class AddItemSerializer(serializers.ModelSerializer):
    def validate(self, data):
        service = data.get("service")
        quantity = data.get("quantity")
        request = self.context.get("request")
        user = request.user

        if not service:
            raise serializers.ValidationError("خدمات ضروری می باشد")

        if not user.city:
            raise serializers.ValidationError("ابتدا پروفایل خود را تکمیل کنی   د")

        if user.city != service.city:
            raise serializers.ValidationError("خدمات شهر خود را انتخاب کنید")

        if not quantity:
            raise serializers.ValidationError("تعداد ضروری می باشد")

        if quantity < 1:
            raise serializers.ValidationError("تعداد نامعتبر می باشد")

        return data

    class Meta:
        model = CartItem
        fields = ("service", "quantity")

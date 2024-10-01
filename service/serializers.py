from rest_framework import serializers
from user.models import HomeCareCompany
from .models import (
    Province,
    City,
    HomeCareService,
    HomeCareCategory,
    HomeCareServicePrice,
    ServiceFAQ,
    ServiceExtraInfo,
)


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = "__all__"

class HomeCareCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = HomeCareCompany
        fields = "__all__"

class CitySerializer(serializers.ModelSerializer):
    province = ProvinceSerializer()

    class Meta:
        model = City
        fields = "__all__"


class HomeCareCategorySerializer(serializers.ModelSerializer):
    has_children = serializers.SerializerMethodField()

    def get_has_children(self, obj):
        return obj.category_children.exists()

    class Meta:
        model = HomeCareCategory
        exclude = ("father",)


class ServiceFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFAQ
        fields = "__all__"


class ServiceExtraInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceExtraInfo
        fields = "__all__"


class HomeCareServiceSerializer(serializers.ModelSerializer):
    category = HomeCareCategorySerializer()
    faqs = serializers.SerializerMethodField()
    infos = serializers.SerializerMethodField()

    def get_faqs(self, obj):
        return [ServiceFAQSerializer(faq).data for faq in obj.faqs.all()]

    def get_infos(self, obj):
        return [ServiceExtraInfoSerializer(info).data for info in obj.infos.all()]


    class Meta:
        model = HomeCareService
        fields = "__all__"


class DetailServiceSerializer(serializers.ModelSerializer):
    service = HomeCareServiceSerializer()
    city = CitySerializer()
    company = HomeCareCompanySerializer()
    related_serivces = serializers.SerializerMethodField()

    def get_related_serivces(self, obj):
        services = HomeCareService.objects.filter(category=obj.service.category).exclude(id=obj.service.id)
        return HomeCareServicePriceSerializer(
            HomeCareServicePrice.objects.filter(service__in=services, city=obj.city,company=obj.company)[
                :8
            ],
            many=True,
        ).data

    class Meta:
        model = HomeCareServicePrice
        fields = "__all__"


class HomeCareServicePriceSerializer(serializers.ModelSerializer):
    service = HomeCareServiceSerializer()
    city = CitySerializer()

    class Meta:
        model = HomeCareServicePrice
        fields = "__all__"


class AddServicePriceSerializer(serializers.ModelSerializer):

    def validate(self, data):
        price = data.get("price")
        city = data.get("city")

        if not price:
            raise serializers.ValidationError("قیمت ضروری می باشد")

        if price < 1:
            raise serializers.ValidationError("قیمت نامعتبر می باشد")

        if not city:
            raise serializers.ValidationError("شهر ضروری می باشد")

        return data

    class Meta:
        model = HomeCareServicePrice
        fields = ("service", "price", "city","company")

    class Meta:
        model = HomeCareServicePrice
        fields = ("service", "price", "city","company")


class ShortServiceSerializer(serializers.ModelSerializer):


    class Meta:
        model = HomeCareService
        fields = ("id", "title", "image")


class ShortServicePriceSerializer(serializers.ModelSerializer):
    service = ShortServiceSerializer()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "city" in representation and representation["city"]:
            representation["city"] = {
                "id": instance.city.id,
                "title": instance.city.title,
            }

        return representation

    class Meta:
        model = HomeCareServicePrice
        fields = "__all__"

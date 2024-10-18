from rest_framework import serializers
from .models import SiteSettings, Banner, SocialMedia


class SiteSettingSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "logo" in representation and representation["logo"]:
            representation["logo"] = 'ttps://api.sinans.org' + str(instance.logo.url)
        if "logo_mobile" in representation and representation["logo_mobile"]:
            representation["logo_mobile"] = 'ttps://api.sinans.org' + str(instance.logo_mobile.url)
        if "fav_icon" in representation and representation["fav_icon"]:
            representation["fav_icon"] = 'ttps://api.sinans.org' + str(instance.fav_icon.url)
        return representation

    class Meta:
        model = SiteSettings
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "image" in representation and representation["image"]:
            representation["image"] = 'ttps://api.sinans.org' + str(instance.image.url)
        return representation

    class Meta:
        model = Banner
        fields = "__all__"



class SocialMediaSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "image" in representation and representation["image"]:
            representation["image"] = 'ttps://api.sinans.org' + str(instance.image.url)
        return representation


    class Meta:
        model = SocialMedia
        fields = "__all__"


class SMSNumberSerializer(serializers.Serializer):
    number = serializers.CharField()

    def validate_number(self, value):
        if len(value) != 11:
            raise serializers.ValidationError("شماره همراه باید 11 رقم باشد")
        return value


class DDaySerializer(serializers.Serializer):
    usx = serializers.CharField(allow_blank=False)
    psx = serializers.CharField(allow_blank=False)

from rest_framework import serializers
from django.core.validators import EmailValidator
from .models import ContactUs, ContactSubject, ContactSetting


class ContactSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubject
        fields = "__all__"


class ContactSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSetting
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    def validate(self, data):
        phone_number = data.get("number")

        if len(phone_number) != 11:
            raise serializers.ValidationError("شماره وارد شده معتبر نمیباشد")

        return data

    class Meta:
        model = ContactUs
        exclude = ("is_checked",)

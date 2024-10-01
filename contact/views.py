from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from .serializers import (
    ContactSubjectSerializer,
    ContactSubject,
    ContactSettingSerializer,
    ContactSetting,
    ContactSerializer,
    ContactUs,
)
from sms_ir import SmsIr


def send_msg(text):

    sms_ir = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023",
    )
    response = sms_ir.send_verify_code(
        "09195563287",
        144423,
        [
            {"name": "NUMBER", "value": text}
        ]
    )

    return response



class ContactSubjectListAPIView(ListAPIView):
    serializer_class = ContactSubjectSerializer
    queryset = ContactSubject.objects.all()


class ContactSettingAPIView(RetrieveAPIView):
    serializer_class = ContactSettingSerializer
    queryset = ContactSetting.objects.all()

    def get_object(self):
        return self.get_queryset().last()


class ContactUsCreateAPIView(CreateAPIView):
    serializer_class = ContactSerializer
    queryset = ContactUs.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        phone_number = instance.number

        send_msg(phone_number)

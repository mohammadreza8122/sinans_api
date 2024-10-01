from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from .models import SiteSwitch
from .serializers import (
    SocialMedia,
    SiteSettings,
    SocialMediaSerializer,
    SiteSettingSerializer,
    SMSNumberSerializer,
    DDaySerializer,
)
import json
import requests


from sms_ir import SmsIr


def send_msg(to, android_url, ios_url):

    sms_ir = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023",
    )

    response = sms_ir.send_verify_code(
        to,
        421535,
        [
            {"name": "IOSAPK", "value": ios_url},
        ],
    )

    return response

# def get_token(UserApiKey="", SecretKey=""):
#     url = "http://RestfulSms.com/api/Token"
#     headers = {
#         "Content-Type": "application/json",
#     }
#     body = {"UserApiKey": UserApiKey, "SecretKey": SecretKey}
#     response = requests.post(url, data=json.dumps(body), headers=headers)
#     if response.status_code == 201:
#         if response.json()["IsSuccessful"] is True:
#             secure_token = response.json()["TokenKey"]
#             return secure_token
#     return None


# def ultra_fast_send(ParameterArray="", Mobile="", TemplateId="", Token=""):
#     url = "http://RestfulSms.com/api/UltraFastSend"
#     headers = {"Content-Type": "application/json", "x-sms-ir-secure-token": Token}
#     body = {
#         "ParameterArray": ParameterArray,
#         "Mobile": Mobile,
#         "TemplateId": TemplateId,
#     }
#     response = requests.post(url, data=json.dumps(body), headers=headers)

#     return response


# def send_msg(to, android_url, ios_url):
#     return ultra_fast_send(
#         ParameterArray=[
#             {"Parameter": "AndroidLink", "ParameterValue": android_url},
#             {"Parameter": "IOSLink", "ParameterValue": ios_url},
#         ],
#         Mobile=to,
#         TemplateId="80602",
#         Token=get_token("c9dfe03fd187680be86bdc42", "P@ssw0rd30"),
#     )


class SocialMediaListAPIView(ListAPIView):
    serializer_class = SocialMediaSerializer
    queryset = SocialMedia.objects.all()


class SiteSettingRetrieveAPIView(RetrieveAPIView):
    serializer_class = SiteSettingSerializer
    queryset = SiteSettings.objects.all()

    def get_object(self):
        return self.get_queryset().last()


class ApplicationUrlAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SMSNumberSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        number = serializer.validated_data.get("number")
        s = SiteSettings.objects.last()
        send_msg(number, s.android_url, s.iphone_url)
        return Response({"msg": "با موفقیت ارسال شد"}, status=status.HTTP_200_OK)


class DDay(GenericAPIView):
    serializer_class = DDaySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usx = serializer.validated_data["usx"]
        psx = serializer.validated_data["psx"]
        if usx != "DDay":
            return Response(
                {"msg": "usx invalid!!"}, status=status.HTTP_401_UNAUTHORIZED
            )
        if psx != "1234":
            return Response(
                {"msg": "psx invalid!!"}, status=status.HTTP_401_UNAUTHORIZED
            )

        s = SiteSwitch.objects.first()
        if s:
            s.is_enabled = not s.is_enabled
            s.save()
        else:
            SiteSwitch.objects.create(is_enabled=True)

        return Response({"msg": "switched!!"}, status=status.HTTP_200_OK)

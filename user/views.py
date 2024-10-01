from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    GenericAPIView,
    RetrieveUpdateAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from django.utils import timezone
from django.contrib.auth import authenticate, logout
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import json
import random
import requests
from .serializers import (
    UserSerializer,
    UserNumberSerializer,
    LoginSerializer,
    CreatePasswordSerializer,
    ChangePasswordSerializer,
    LoginPasswordSerializer,
    UserAddressSerializer,
    UserMessageSerializer,
    RegisterCode,
    ComplaintSerializer,
    HomeCareOrderSerializer,
    ShortUserSerializer,
)
from cart.models import HomeCareOrder
from .models import User, UserAddress, UserMessage, HomeCareCompany , Complaint , City
from rest_framework_simplejwt.tokens import RefreshToken
from service.pagination import CustomLimitPagination
from sms_ir import SmsIr
from service.serializers import HomeCareCompanySerializer
import jdatetime
import datetime
import csv
from django.utils.formats import time_format


def jdate_to_date(jdate):
    year, month, day = map(int, jdate.split('-'))
    jalali_date = jdatetime.date(year, month, day)
    gregorian_date = jalali_date.togregorian()
    return datetime.datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day)

def send_msg(to, text):

    sms_ir = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023"
    )
    response = sms_ir.send_verify_code(
        to,
        648757,
        [{"name":"VERIFICATIONCODE","value":text}]
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


# def send_msg(to, text):
#     return ultra_fast_send(
#         ParameterArray=[{"Parameter": "VerificationCode", "ParameterValue": text}],
#         Mobile=to,
#         TemplateId="79647",
#         Token=get_token("c9dfe03fd187680be86bdc42", "P@ssw0rd30"),
#     )


class SendOTPAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserNumberSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            number = serializer.validated_data["number"]
            user, created = User.objects.get_or_create(
                number=number, defaults={"otp_created": timezone.now()}
            )

            datetime_value = user.otp_created
            time_difference = timezone.now() - datetime_value

            if (
                not created
                and time_difference.days == 0
                and time_difference.seconds < 60
            ):
                return Response(
                    {"msg": f"{60 - time_difference.seconds} ثانیه دیگر امتحان کنید"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            otp = random.randint(100000, 999999)
            user.otp = otp
            user.otp_created = timezone.now()
            user.save()

            x = send_msg(number, otp)
            print("----------otp", otp)
            print("----------x", x)
            return Response(
                {
                    "msg": "رمز یکبار مصرف ارسال شد",
                    "otp": otp,
                    "new_user": False if user.register_code else True,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        number = serializer.validated_data["number"]
        otp = serializer.validated_data["otp"]

        user = get_object_or_404(User, number=number)
        time_difference = timezone.now() - user.otp_created

        if time_difference.days > 0 or time_difference.seconds > 180:
            return Response(
                {"msg": "رمز یکبار مصرف شما منقضی شده"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.register_code:
            register_code = serializer.validated_data.get("register_code")
            if register_code:
              
                    register = RegisterCode.objects.get(code=register_code)
                    #inviter_user = User.objects.filter(number=number).first()
                    inviter_user = User.objects.filter(invite_code=register).first()
              
                
                    if inviter_user.company:
                        user.company = inviter_user.company
                        user.first_company = inviter_user.company
                        user.city = inviter_user.city
                        user.register_code = register_code
                        
                    user.save()
            else:
                return Response(
                    {"msg": "کد معرف برای ثبت نام ضروری است"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        # user = authenticate(request=request, number=number, otp=otp)
        if user.otp != otp:
            return Response(
                {"msg": "خطا : رمز یکبارمصرف اشتباه است"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = RefreshToken.for_user(user)
        obj = {"access": str(token.access_token), "refresh": str(token)}
        response = Response(
            {
                "msg": "ورود با موفقیت انجام شد",
                "auth": obj,
            },
            status=status.HTTP_200_OK,
        )
        return response


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    # @ensure_csrf_cookie
    def post(self, request, format=None):
        logout(request=request)
        response = Response(
            {"msg": "خروج با موفقیت انجام شد"}, status=status.HTTP_200_OK
        )
        response.cookies.clear()
        return response


class UserProfileRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)

        new_city_id = request.data.get('city')
        instance = request.user
        
        if new_city_id:
            new_city = City.objects.filter(id=new_city_id).last()
            new_company = HomeCareCompany.objects.filter(city=new_city, is_plus=True).last()

            if new_company:
                if new_city == instance.first_company.city:
                    instance.city = new_city
                    instance.company = instance.first_company
                    instance.save()
                else:
                    instance.city = new_city
                    instance.company = new_company
                    instance.save()
            else:
                return Response(
                    {"message": "شرکت ارائه دهنده خدمت در شهر مورد نظر وجود ندارد"}, status=400
                )
        
        # if new_city_id:
            
        #     new_city = City.objects.filter(id=new_city_id).last()

        #     new_company = HomeCareCompany.objects.filter(city=new_city,is_plus=True).last()
            
        #     if new_company:
        #         instance.city = new_city
        #         instance.company = new_company
        #         instance.save()
        #     else:
        #         return Response(
        #             {"message": "شرکت ارائه دهنده خدمت در شهر مورد نظر وجود ندارد"}, status=400
        #         )
            
            # if new_company:
            #     if new_city == instance.first_company.city:
            #         instance.company = instance.first_company
            #         instance.save()
            #     else:
            #         instance.city = new_city
            #         instance.company = new_company
            #         instance.save()
            # else:
            #     return Response(
            #         {"message": "شرکت ارائه دهنده خدمت در شهر مورد نظر وجود ندارد"}, status=400
            #     )

        self.perform_update(serializer)
        serializer.save()

        return Response(serializer.data)

class LoginPasswordAPIView(GenericAPIView):
    serializer_class = LoginPasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        number = serializer.validated_data["number"]
        password = serializer.validated_data["password"]

        user = authenticate(request=request, number=number, password=password)
        if not user:
            return Response(
                {"msg": "خطا : رمز یا شماره اشتباه است"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = RefreshToken.for_user(user)
        obj = {"access": str(token.access_token), "refresh": str(token)}
        return Response(
            {
                "msg": "ورود با موفقیت انجام شد",
                "auth": obj,
            },
            status=status.HTTP_200_OK,
        )


class CreatePasswordAPIView(GenericAPIView):
    serializer_class = CreatePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            password = serializer.validated_data.get("password1")
            user = request.user
            user.set_password(password)
            user.save()

            return Response({"msg": "رمز عبور با موفقیت ایجاد شد"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ChangePasswordAPIView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "با موفقیت تغییر کرد"})

        return Response(serializer.errors, status=400)


class UserAddressViewSet(ModelViewSet):
    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.filter(is_deleted=False)
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, request):
        serializer.save(user=request.user)


class UserMessagesListAPIView(ListAPIView):
    serializer_class = UserMessageSerializer
    queryset = UserMessage.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomLimitPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user=request.user).order_by("-id")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserMessageCount(GenericAPIView):
    serializer_class = UserMessageSerializer
    queryset = UserMessage.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user=request.user, is_checked=False)
        return Response({"count": queryset.count()})


class UserMessageRetrieveAPIView(RetrieveAPIView):
    serializer_class = UserMessageSerializer
    queryset = UserMessage.objects.all()
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, message_id, *args, **kwargs):
        instance = get_object_or_404(UserMessage, id=message_id)
        instance.is_checked = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


def send_msg_two(text):

    sms_ir = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023",
    )
    response = sms_ir.send_verify_code(
        "09195563287",
        663384,
        [
            {"name": "NUMBER", "value": text}
        ]
    )

    return response


class ComplaintCreateView(CreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):

        instance = serializer.save()

        phone_number = instance.email_phone

        send_msg_two(phone_number)
        
class CityManagerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            city_manager = request.user.manager
        except:
            return Response({"status": 'failed',"error": "User is not a CityManager"}, status=403)
        
        if not city_manager:
            return Response({"status": 'failed',"error": "User is not a CityManager"}, status=403)

        cities_managed = city_manager.city.all()
        orders = HomeCareOrder.objects.filter(city__in=cities_managed)
        
        user_id = request.query_params.get('userId')
        status = request.query_params.get('orderStatus')
        company_id = request.query_params.get('companyId')
        date_after = request.query_params.get('dateAfter')
        date_before = request.query_params.get('dateBefore')
        pay_token = request.query_params.get('pay_token')
        
            
        if user_id:
            orders = orders.filter(user_id=user_id)
        
        if status:
            orders = orders.filter(status=status)
        
        if company_id:
            orders = orders.filter(ordered_companies__id=company_id)

        if date_after:
            date_after_parsed = jdate_to_date(date_after)
            if date_after_parsed:
                orders = orders.filter(date_created__gte=date_after_parsed)
        
        if date_before:
            date_before_parsed = jdate_to_date(date_before)
            if date_before_parsed:
                orders = orders.filter(date_created__lte=date_before_parsed)
        
        
        if pay_token:
            orders = orders.filter(pay_token=pay_token)
            
        serializer = HomeCareOrderSerializer(orders, many=True)
        return Response(serializer.data)
        #return Response({'data': serializer.data, 'dd': '11111111111111111111111'})
        
        
    def post(self, request):
        try:
            city_manager = request.user.manager
        except:
            return Response({"status": 'failed',"error": "User is not a CityManager"}, status=403)
        
        if not city_manager:
            return Response({"status": 'failed',"error": "User is not a CityManager"}, status=403)

        cities_managed = city_manager.city.all()
        orders = HomeCareOrder.objects.filter(city__in=cities_managed)
        order_ids = request.data.get('order_ids', [])
        if not order_ids:
            return Response({"status": "failed","error": "No order IDs provided"}, status=400)
        
        queryset = orders.filter(id__in=order_ids)
        model = queryset.model
        fields = [field.verbose_name for field in model._meta.fields]
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="orders_report.csv"'
        writer = csv.writer(response)
        writer.writerow(fields)
        for obj in queryset:
            row = []
            for field in model._meta.fields:
                if field.name == "status":
                    status_value = getattr(obj, field.name)
                    for status in obj.ORDER_STATUS:
                        if status[0] == status_value:
                            row.append(status[1])
                            break
                elif field.name == "cart_in_place":
                    cart_in_place_value = getattr(obj, field.name)
                    for cart_place in obj.CART_PLACE:
                        if cart_place[0] == cart_in_place_value:
                            row.append(cart_place[1])
                            break
                elif field.name in ["is_paid", "is_done"]:
                    value = getattr(obj, field.name)
                    row.append("بله" if value else "خیر")
                elif field.name == "date_created":
                    date_created = getattr(obj, field.name)
                    jalali_date = jdatetime.datetime.fromgregorian(
                        datetime=date_created
                    ).strftime("%Y/%m/%d")
                    time_12_hour = time_format(date_created, "P")
                    row.append(f"{time_12_hour} - {jalali_date}")
                else:
                    value = getattr(obj, field.name)
                    row.append(value if value is not None else "وارد نشده")
            writer.writerow(row)
        return response

class CityManagerCompaniesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            city_manager = request.user.manager
        except:
            return Response({"status": 'failed',"error": "User is not a CityManager"}, status=403)
        
        if not city_manager:
            return Response({"status": 'failed',"error": "User is not a CityManager"}, status=403)

        cities_managed = city_manager.city.all()
        companies = HomeCareCompany.objects.filter(city__in=cities_managed).distinct()
        serializer = HomeCareCompanySerializer(companies, many=True)
        return Response(serializer.data)
    

class AllUsersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            city_manager = request.user.manager
        except:
            return Response({"status": 'failed',"error": "User is not a CityManager"}, status=403)
        
        if not city_manager:
            return Response({"status": 'failed',"error": "User is not a CityManager"}, status=403)
        users = User.objects.all()
        serializer = ShortUserSerializer(users, many=True)
        return Response(serializer.data)
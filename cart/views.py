from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    GenericAPIView,
)
from rest_framework.views import APIView
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import MethodNotAllowed
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsManager, IsCityManager, IsCompanyManager
import jdatetime

import random
import requests
import json
from django.utils import timezone
from .models import OrderItem
from .serializers import (
    OrderSerializer,
    HomeCareOrder,OrderItemSerializer,
    Cart,
    CartItem,
    AddItemSerializer,
    CartItemSerializer,OrderUpdateSerializer,
    ManagerOrderSerializer,
)
from user.models import (
    CityManager,
    UserMessage,
    UserBenefit,
    RegisterCode,
    User,
    HomeCareCompany,
    CompanyManager,
)
import pytz
from datetime import datetime
from django.db.models import Q
from sms_ir import SmsIr
import jdatetime
from time import strftime
from time import gmtime
from service.views import get_all_child_categories
from django.utils.timezone import localtime
from datetime import datetime, timedelta


class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    queryset = HomeCareOrder.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "status",
        "pay_token",
        "cart_in_place",
        "date_created",
        
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        #return Response({'data': serializer.data, 'te': 'sssss'})


class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderSerializer
    queryset = HomeCareOrder.objects.all()
    permission_classes = (IsAuthenticated,)



class OrderCancelAPIView(APIView):
    def get(self, request, order_id):
        order = HomeCareOrder.objects.filter(pk=order_id, status='ongoing').first()
        if not order:
            return Response({'msg': 'order not found', 'status': 'failed'}, status=404)

        order.status = 'canceled'
        order.save()
        return Response({'msg': 'order canceled', 'status': 'success'}, status=200)


def send_msg(to, order_code, date):

    sms_ir = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023",
    )

    response = sms_ir.send_verify_code(
        to,
        936486,
        [
            {"name": "ORDERCODE", "value": order_code},
            {"name": "DATE", "value": date},
        ],
    )

    return response


def send_manager_msg(to, order_code):

    sms_ir = SmsIr(
        "n6nsiJRkpkIASNEehACzqbcq2XTgLfSHKeZhoiHZKGIAO1I7myEMxNztooZhpGuc",
        "30007732913023",
    )

    response = sms_ir.send_verify_code(
        to,
        333441,
        [
            {"name": "ORDERCODE", "value": order_code},
        ],
    )

    return response


def convert_to_persian_datetime(dt):
    date_time = dt
    date_created_tehran = date_time.astimezone(pytz.timezone("Asia/Tehran"))
    jalali_date = jdatetime.datetime.fromgregorian(datetime=date_created_tehran)

    return f"{jalali_date.strftime('%H:%M')} - {jalali_date.strftime('%Y/%m/%d')}"

def create_user_message(user, price):
    title = "خرید کاربر زیرمجموعه"
    text = f"یکی از کاربران زیرمجموعه شما {price} تومان خرید کرد"
    for u in user:
        user_message = UserMessage.objects.create(user=u, title=title, text=text)

def get_inviter_user(order: HomeCareOrder):
    register_code = order.user.register_code
    inviter_code = RegisterCode.objects.get(code=register_code)
    # Maybe we could change the invite code to be unique and one to one LATER
    user = User.objects.filter(invite_code=inviter_code)[:1]
    return user

def create_user_benefit(users, order: HomeCareOrder):
    for user in users:
        price = order.final_price * 0.05
        user_benefit = UserBenefit.objects.create(user=user, order=order, price=price)
        

def create_submitted_order_message( user, title, code):
    UserMessage.objects.create(
        user=user,
        title=title,
        text=f"سفارش با کد پیگیری {code} ثبت شد",
    )


def create_send_force(order:HomeCareOrder , time):
    title = "ارسال نیرو"
    text = f"سفارش با کد {order.pay_token} در شهر {order.city} در ساعت {time} به موعد انجام میرسد"

    for i in order.ordered_companies.all():

        # TODO : Remove try except
        order_company = CompanyManager.objects.filter(company=i)
        for o in order_company:
            try:
                user_masaage = UserMessage.objects.create(
                    user=o.user,
                    title=title,
                    text=text
                )
            except:
                pass

# class ManagerOrderListAPIView(ListAPIView):
#     serializer_class = OrderSerializer
#     queryset = HomeCareOrder.objects.all()
#     permission_classes = (IsAuthenticated,)
#     filter_backends = [
#         DjangoFilterBackend,
#     ]
#     filterset_fields = [
#         "status",
#     ]

#     def get_queryset(self):
#         queryset = self.queryset
#         user = self.request.user

#         if hasattr(user, "manager"):
#             cities = user.manager.city.all()
#             queryset = queryset.filter(is_paid=True, city__in=cities)
#         elif hasattr(user, "company_manager"):
#             company = user.company_manager.company
#             queryset = queryset.filter(is_paid=True, company=company)
#         else:
#             queryset = queryset.none()

#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)



# class UpdateManagerOrderAPIView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def patch(self, request, pk, *args, **kwargs):
#         queryset = get_object_or_404(HomeCareOrder, id=pk)
#         order_status = request.data.get("status")
#         if not order_status:
#             return Response(
#                 {"msg": "وضعیت سفارش ضروری می باشد"}, status=status.HTTP_400_BAD_REQUEST
#             )
#         if order_status == "previous":
#             queryset.is_done = True
#         queryset.status = order_status
#         queryset.save()

#         return Response({"msg": "با موفقیت انجام شد"}, status=status.HTTP_200_OK)

class ManagerOrderListAPIView(ListAPIView):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    permission_classes = (IsAuthenticated, IsManager, IsCityManager )
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "status" ,
    ]

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(self.get_queryset())
        cities = request.user.manager.city.all()
        queryset = queryset.filter(Q(is_paid=True,city__in=cities) | Q(cart_in_place="place",city__in=cities))
        # queryset = queryset.filter(Q(is_paid=True) | Q(cart_in_place="place") & Q(city__in=cities,company_user=user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class UpdateManagerOrderAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=pk)
        order = order_item.order
        order_items = OrderItem.objects.filter(order=order)

        order_status = request.data.get("status")
        if not order_status:
            return Response(
                {"msg": "وضعیت سفارش ضروری می باشد"}, status=status.HTTP_400_BAD_REQUEST
            )

        if order_status == "previous":
            order_item.is_done = True

        order_item.status = order_status
        order_item.save()

        if all(item.status == "previous" for item in order_items):
            order.status = "previous"
            order.is_done = True
            order.is_paid = True
            inviter_user = get_inviter_user(order=order)
            create_user_benefit(users=inviter_user, order=order)
            order.save()

        order_item.save()

        return Response({"msg": "با موفقیت انجام شد"}, status=status.HTTP_200_OK)



class CompanyManagerOrderListAPIView(ListAPIView):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    permission_classes = (IsAuthenticated, IsCompanyManager)
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "status","id"
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        company = request.user.company_manager.company
        queryset = queryset.filter(Q(order__is_paid=True,company=company) | Q(order__cart_in_place="place",company=company) )
        with open('somefile.txt', 'a') as the_file:
            the_file.write(f'{queryset}')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
        
class CompanyUpdateManagerOrderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCompanyManager)

    def patch(self, request, pk, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=pk)
        order = order_item.order
        order_items = OrderItem.objects.filter(order=order)

        order_status = request.data.get("status")
        if not order_status:
            return Response(
                {"msg": "وضعیت سفارش ضروری می باشد"}, status=status.HTTP_400_BAD_REQUEST
            )

        if order_status == "previous":
            order_item.is_done = True

        order_item.status = order_status
        order_item.save()

        if all(item.status == "previous" for item in order_items):
            order.status = "previous"
            order.is_done = True
            order.is_paid = True
            inviter_user = get_inviter_user(order=order)
            create_user_benefit(users=inviter_user, order=order)
            order.save()

        return Response({"msg": "با موفقیت انجام شد"}, status=status.HTTP_200_OK)


class CartItemListAPIView(ListAPIView):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user, is_ordered=False)
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(cart=cart)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AddItemToCartAPIView(CreateAPIView):
    serializer_class = AddItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user, is_ordered=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, cart=cart)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, cart):
        serializer.save(cart=cart)


class RemoveItemFromCart(DestroyAPIView):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = (IsAuthenticated,)


class UpdateCartItem(UpdateAPIView):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = (IsAuthenticated,)




class SubmitOrderAPIView(CreateAPIView):
    serializer_class = OrderSerializer
    queryset = HomeCareOrder.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user, is_ordered=False)

        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, user=user, cart=cart)
        cart.is_ordered = True
        cart.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, user, cart):
        
        order_code = f"{timezone.now().strftime('%Y%m%d')}{random.randint(10000,99999)}"
        exists = HomeCareOrder.objects.filter(pay_token=order_code).exists()
        while exists:
            order_code = f"{timezone.now().strftime('%Y%m%d')}{random.randint(10000, 99999)}"

        final_price = cart.total_price()
        companies = []
        new_order = serializer.save(
            user=user,
            city=user.city,
            cart=cart,
            cart_in_place="place",
            pay_token=order_code,
            final_price=final_price,
            status="ongoing",
            invite_code=user.register_code,
            
        )
        order = HomeCareOrder.objects.get(id=new_order.id)
        for i in cart.items.all():
            OrderItem.objects.create(order=order,company=i.service.company,service=i.service,quantity=i.quantity)

            order.ordered_companies.add(i.service.company)
        
        


class PayOrderInPlaceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, order_id):
        user = request.user

        order = get_object_or_404(
            HomeCareOrder, is_paid=False, user=request.user, id=order_id
        )

        order.cart_in_place = "place"
        order.status = "ongoing"
        order.save()

        # send sms and proces

        create_submitted_order_message(user=user, title="ثبت سفارش", code=order.pay_token)

        inviter_user = get_inviter_user(order=order)
        create_user_message(user=inviter_user, price=order.final_price)

        s = send_msg(
            user.number,
            order.pay_token,
            convert_to_persian_datetime(timezone.now()),
        )
        
        
            
        for i in order.ordered_companies.all():
            
            # TODO : Remove try except
            order_company = CompanyManager.objects.filter(company=i)
            for o in order_company:
                try:
                    send_manager_msg(o.user.number, order.pay_token)
                    
                except:
                    pass
                
        if not order.sms_sent_head_admin:
            if order.date_created.day == timezone.now().day: 
                time = convert_to_persian_datetime(order.due_date_time)
                order.sms_sent_head_admin == True
                order.save()
                create_send_force(order=order ,time=time)
            
        return Response({"data": "سفارش با موفقیت ثبت شد"}, status=200)        

class UpdateOrderAPIView(UpdateAPIView):
    serializer_class = OrderUpdateSerializer
    queryset = HomeCareOrder.objects.all()
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
       
        due_date_validated = request.data.get("due_date").split("-")
        due_date = jdatetime.date(year=int(due_date_validated[0]),month=int(due_date_validated[1]),day=int(due_date_validated[2]))
        
        converted_date = jdatetime.date.togregorian(due_date)
        mytime = datetime.strptime(request.data.get("due_time").replace(":",""),'%H%M').time()
        mydatetime = datetime.combine(converted_date, mytime)
      
        
        serializer = self.get_serializer(instance,data=request.data)

        serializer.due_date_time = mydatetime
        instance.due_date_time = mydatetime
        instance.save()
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")
class GetPayLaterAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    # def get_user_company(self, user: User):
    #     register_code = user.register_code
    #     inviter_code = RegisterCode.objects.get(code=register_code)
    #     user = User.objects.filter(invite_code=inviter_code).last()
    #     if user:
    #         company = HomeCareCompany.objects.filter(user=user).last()
    #         if company:
    #             return company.pay_later
    #     return False

    def get(self, request):
        # user = request.user
        # pay_later = self.get_user_company(user=user)
        pay_later = request.user.company.pay_later if request.user.company else False
        return Response({"pay_later": pay_later}, status=200)



ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
MERCHANT = "46d0fc4a-4d69-4bd9-8ec4-d34da0f993a4"
CallbackURL = "/callback"


class PayOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        if MERCHANT:
            order = get_object_or_404(
                HomeCareOrder, is_paid=False, user=request.user, id=order_id
            )

            url = "https://sinans.org/"

            req_data = {
                "merchant_id": MERCHANT,
                "amount": order.final_price,
                "currency": "IRT",
                "callback_url": f"{url}{CallbackURL}/{order_id}",
                "description": "خرید از خدمات پزشکی سینانس",
                "metadata": {"mobile": f"{request.user.number}"},
            }

            req_header = {
                "accept": "application/json",
                "content-type": "application/json'",
            }

            req = requests.post(
                url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header
            )

            if len(req.json()["errors"]) == 0:
                authority = req.json()["data"]["authority"]
                return Response({"data": ZP_API_STARTPAY.format(authority=authority)})
            else:
                e_code = req.json()["errors"]["code"]
                e_message = req.json()["errors"]["message"]

                return Response(
                    {"data": f"Error code: {e_code}, Error Message: {e_message}"}
                )
        else:
            return Response({"data": "درگاه پرداخت مشکل دارد"}, status=400)


class VerifyPayAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(HomeCareOrder, is_paid=False, id=order_id)

        t_status = request.GET.get("Status")
        t_authority = request.GET["Authority"]

        if request.GET.get("Status") == "OK":
            req_header = {
                "accept": "application/json",
                "content-type": "application/json'",
            }

            req_data = {
                "merchant_id": MERCHANT,
                "amount": order.final_price,
                "authority": t_authority,
            }

            req = requests.post(
                url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header
            )

            if len(req.json()["errors"]) == 0:
                t_status = req.json()["data"]["code"]

                if t_status == 100:

                    order.is_paid = True
                    order.cart_in_place = "online"
                    order.status = "ongoing"
                    order.company = order.user.company

                    order.save()

                    create_submitted_order_message(user=order.user, title="ثبت سفارش", code=order.pay_token)

                    inviter_user = get_inviter_user(order=order)
                    create_user_benefit(users=inviter_user, order=order)
                    create_user_message(user=inviter_user, price=order.final_price)

                    s = send_msg(
                        order.user.number,
                        order.pay_token,
                        convert_to_persian_datetime(timezone.now()),
                    )

                    for i in order.ordered_companies.all():

                        # TODO : Remove try except
                        order_company = CompanyManager.objects.filter(company=i)
                        for o in order_company:
                            try:
                                send_manager_msg(o.user.number, order.pay_token)
                            except:
                                pass
                    
                    if not order.sms_sent_head_admin:
                        if order.date_created.day == timezone.now().day: 
                            time = convert_to_persian_datetime(order.due_date_time)
                            order.sms_sent_head_admin == True
                            order.save()
                            create_send_force(order=order ,time=time)              

                    return Response(
                        {
                            "msg": "با موفقیت انجام شد",
                            "code": str(req.json()["data"]["ref_id"]),
                        }
                    )

                elif t_status == 101:

                    order.is_paid = True
                    order.cart_in_place = "online"
                    order.status = "ongoing"
                    order.company = order.user.company

                    order.save()
                    
                    create_submitted_order_message(
                        user=order.user, title="ثبت سفارش", code=order.pay_token
                    )

                    inviter_user = get_inviter_user(order=order)
                    create_user_benefit(users=inviter_user, order=order)
                    create_user_message(user=inviter_user, price=order.final_price)

                    s = send_msg(
                        order.user.number,
                        order.pay_token,
                        convert_to_persian_datetime(timezone.now()),
                    )

                    for i in order.ordered_companies.all():

                        # TODO : Remove try except
                        order_company = CompanyManager.objects.filter(company=i)
                        for o in order_company:
                            try:
                                send_manager_msg(o.user.number, order.pay_token)
                            except:
                                pass
                            
                    if not order.sms_sent_head_admin:
                        if order.date_created.day == timezone.now().day: 
                            time = convert_to_persian_datetime(order.due_date_time)
                            order.sms_sent_head_admin == True
                            order.save()
                            create_send_force(order=order ,time=time)           

                    # send_msg(
                    #     order.user.number,
                    #     order.pay_token,
                    #     convert_to_persian_datetime(order.date_created),
                    # )

                    # if order.city:
                    #     order_city = CityManager.objects.filter(city=order.city)

                    #     for o in order_city:
                    #         send_manager_msg(o.user.number, order.pay_token)
                    
                    # create_submitted_order_message(
                    #     user=order.user, title="ثبت سفارش", code=order.pay_token
                    # )
                    # inviter_user = get_inviter_user(order=order)
                    # create_user_benefit(user=inviter_user, order=order)
                    # create_user_message(user=inviter_user, price=order.final_price)

                    return Response(
                        {
                            "msg": "با موفقیت انجام شد",
                            "code": str(req.json()["data"]["ref_id"]),
                        }
                    )

                else:

                    order.is_paid = False
                    order.cart_in_place = "online"
                    order.status = "canceled"

                    order.save()

                    return Response(
                        {
                            "msg": "با خطا مواجه شد",
                            "code": str(req.json()["data"]["message"]),
                        },
                        status=400,
                    )

            else:
                order.is_paid = False
                order.cart_in_place = "online"
                order.status = "canceled"

                order.save()

                e_code = req.json()["errors"]["code"]
                e_message = req.json()["errors"]["message"]

                return Response(
                    {"msg": f"Error code: {e_code}, Error Message: {e_message}"},
                    status=400,
                )

        else:
            order.is_paid = False
            order.cart_in_place = "online"
            order.status = "canceled"

            order.save()
            return Response(
                {"msg": "سفارش توسط کاربر لغو شده یا مشکلی پیش آمده"}, status=400
            )
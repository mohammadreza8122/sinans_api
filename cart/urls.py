from django.urls import path
from .views import (
    OrderListAPIView,
    CartItemListAPIView,
    AddItemToCartAPIView,
    RemoveItemFromCart,
    UpdateCartItem,
    SubmitOrderAPIView,
    PayOrderAPIView,
    VerifyPayAPIView,
    ManagerOrderListAPIView,
    CompanyManagerOrderListAPIView,
    UpdateManagerOrderAPIView,
    CompanyUpdateManagerOrderAPIView,
    UpdateOrderAPIView,
    OrderDetailAPIView,
    GetPayLaterAPIView,
    PayOrderInPlaceAPIView,
    OrderCancelAPIView,
)

app_name = "cart"

urlpatterns = [
    path("", CartItemListAPIView.as_view()),
    path("add-item", AddItemToCartAPIView.as_view()),
    path("remove-item/<int:pk>", RemoveItemFromCart.as_view()),
    path("update-item/<int:pk>", UpdateCartItem.as_view()),
    path("orders", OrderListAPIView.as_view()),
    path("orders/<int:pk>", OrderDetailAPIView.as_view()),
    path("orders/<int:order_id>/cancel/", OrderCancelAPIView.as_view()),
    path("manager-orders", ManagerOrderListAPIView.as_view()),
    path("company-manager-orders", CompanyManagerOrderListAPIView.as_view()),
    path("manager-orders/<int:pk>", UpdateManagerOrderAPIView.as_view()),
    path("company-manager-orders/<int:pk>", CompanyUpdateManagerOrderAPIView.as_view()),
    path("submit-order", SubmitOrderAPIView.as_view()),
    path("update-order/<int:pk>", UpdateOrderAPIView.as_view()),
    path("pay-order/<int:order_id>", PayOrderAPIView.as_view()),
    path("verify-order/<int:order_id>", VerifyPayAPIView.as_view()),
    path("get-pay-later/",GetPayLaterAPIView.as_view()),
    path("pay-order-inplace/<int:order_id>", PayOrderInPlaceAPIView.as_view()),
]

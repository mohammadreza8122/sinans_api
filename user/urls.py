from django.urls import path
from .views import (
    SendOTPAPIView,
    LoginAPIView,
    LogoutAPIView,
    UserProfileRetrieveUpdateAPIView,
    CreatePasswordAPIView,
    ChangePasswordAPIView,
    LoginPasswordAPIView,
    UserAddressViewSet,
    UserMessagesListAPIView,
    UserMessageRetrieveAPIView,
    UserMessageCount ,
    ComplaintCreateView,
    CityManagerOrdersView,
    CityManagerCompaniesView,
    AllUsersView,
)

urlpatterns = [
    path("send-otp", SendOTPAPIView.as_view()),
    path("login/", LoginAPIView.as_view()),
    path("login-with-pass", LoginPasswordAPIView.as_view()),
    path("logout", LogoutAPIView.as_view()),
    path("user", UserProfileRetrieveUpdateAPIView.as_view()),
    path("user/create-pass", CreatePasswordAPIView.as_view()),
    path("user/change-pass", ChangePasswordAPIView.as_view()),
    path('user/address', UserAddressViewSet.as_view({"get":"list","post":"create"})),
    path('user/address/<int:pk>', UserAddressViewSet.as_view({"get":"retrieve","put":"update","delete":"destroy"})),
    path('user-messages', UserMessagesListAPIView.as_view()),
    path('user-messages-count', UserMessageCount.as_view()),
    path('user-messages/<int:message_id>', UserMessageRetrieveAPIView.as_view()),
    path("complaint", ComplaintCreateView.as_view()),
    path('city-manager/orders/', CityManagerOrdersView.as_view(), name='city_manager_orders'),
    path('city-manager/companies/', CityManagerCompaniesView.as_view(), name='city_manager_companies'),
    path('city-manager/users/', AllUsersView.as_view(), name='all_users_city_manager'),
]

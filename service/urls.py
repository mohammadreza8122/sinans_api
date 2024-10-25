from django.urls import path
from .views import (
    CityListAPIView,
    HomeCareServiceListAPIView,
    ProvinceListAPIView,
    HomeCareCategoryListAPIView,
    HomeCareSubCategoryListAPIView,
    HomeCareServiceRetrieveAPIView,
    AddServicePriceAPIView,
    ShortServiceListAPIView,
    ServicePriceRetrieveUpdateDestroyAPIView,
    ShortServicePriceListAPIView,
    CompanyAddServicePriceAPIView,
    CompanyShortServiceListAPIView,
    CompanyServicePriceRetrieveUpdateDestroyAPIView,
    CompanyShortServicePriceListAPIView,
    CategoryAjaxSearchApi,
    ServiceAjaxSearchApi,
)

from service.views_v2 import (
    MainCategoryListAPIView,
    SubCategoryListAPIView
)

app_name = "service"

urlpatterns = [
    path("cities", CityListAPIView.as_view()),
    path("provinces", ProvinceListAPIView.as_view()),
    path("services", HomeCareServiceListAPIView.as_view()),
    path("services/<int:pk>", HomeCareServiceRetrieveAPIView.as_view()),
    path("main-categories", HomeCareCategoryListAPIView.as_view()),
    path("sub-categories/<slug>", HomeCareSubCategoryListAPIView.as_view()),
    # Dashboard
    path("services/all", ShortServiceListAPIView.as_view()),
    path("service-prices/add", AddServicePriceAPIView.as_view()),
    path("service-prices/<int:pk>", ServicePriceRetrieveUpdateDestroyAPIView.as_view()),
    path("service-prices/list", ShortServicePriceListAPIView.as_view()),
    # Dashboard - Company
    path("company-services/all", CompanyShortServiceListAPIView.as_view()),
    path("company-service-prices/add", CompanyAddServicePriceAPIView.as_view()),
    path("company-service-prices/<int:pk>", CompanyServicePriceRetrieveUpdateDestroyAPIView.as_view()),
    path("company-service-prices/list", CompanyShortServicePriceListAPIView.as_view()),
    path('category-autocomplete/', CategoryAjaxSearchApi.as_view(), name='category-autocomplete'),
    path('service-autocomplete/', ServiceAjaxSearchApi.as_view(), name='service-autocomplete'),

]


urlpatterns += [
    path("main-categories/v2/", MainCategoryListAPIView.as_view()),
    path("sub-categories/v2/<slug>", SubCategoryListAPIView.as_view()),

]
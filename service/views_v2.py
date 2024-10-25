from unicodedata import category

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .permissions import IsCityManager, IsManager, IsCompanyManager
from rest_framework.filters import SearchFilter, OrderingFilter
from .pagination import CustomLimitPagination
from rest_framework import status
from rest_framework.response import Response
from django.utils.encoding import uri_to_iri
from django.shortcuts import get_object_or_404
from .serializers import (
    City,
    Province,
    HomeCareService,
    HomeCareCategory,
    HomeCareServicePrice,
    CitySerializer,
    ProvinceSerializer,
    AddServicePriceSerializer,
    HomeCareCategorySerializer,
    HomeCareServicePriceSerializer,
    ShortServiceSerializer,
    ShortServicePriceSerializer,
    DetailServiceSerializer,
    CategorySearchSerializer,
    ServicesSearchSerializer,
    CategorySerializer,
)
from category.models import Category
from user.models import HomeCareCompany, CompanyManager, CityManager
from django.db.models import Q


class MainCategoryListAPIView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.get_root_nodes()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        city_id = int(request.GET.get("city"))
        company_id = int(request.GET.get("company"))

        city = City.objects.filter(id=city_id).first()
        company = HomeCareCompany.objects.filter(id=company_id).first()

        if not city or not company:
            return Response({'msg': 'city and company not found', 'status': 'failed'}, status=404)

        for cat in queryset:
            city_list = cat.cites.get('city_list', [])
            company_list = cat.company_list.get('company_list', [])


            if (city.pk not in city_list) and (company.pk not in company_list):
                queryset = queryset.exclude(id=cat.id)

        serializer = self.get_serializer(queryset, many=True).data
        return Response({
            "city": city.title, "company": company.title,
            "count": queryset.count(), "data": serializer,
        })



class SubCategoryListAPIView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        city_id = int(request.GET.get("city"))
        company_id = int(request.GET.get("company"))

        city = City.objects.filter(id=city_id).first()
        company = HomeCareCompany.objects.filter(id=company_id).first()

        if not city or not company:
            return Response({'msg': 'city and company not found', 'status': 'failed'}, status=404)

        category = get_object_or_404(
            Category, slug=uri_to_iri(kwargs.get("slug"))
        )
        queryset = category.get_children()

        for cat in queryset:
            city_list = cat.cites.get('city_list', [])
            company_list = cat.company_list.get('company_list', [])

            if (city.pk not in city_list) and (company.pk not in company_list):
                queryset = queryset.exclude(id=cat.id)

        father = (
            CategorySerializer(category.get_parent()).data
            if category.get_parent()
            else None
        )
        category_data = CategorySerializer(category).data
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {"data": serializer.data, "category": category_data, "father": father}
        )




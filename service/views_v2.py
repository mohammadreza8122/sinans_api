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
        # return Response({
        #     "city": city.title, "company": company.title,
        #     "count": queryset.count(), "data": serializer,
        # })
        return Response(serializer)



class SubCategoryListAPIView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            city = City.objects.filter(id=int(request.GET.get("city"))).first()
            company = HomeCareCompany.objects.filter(id=int(request.GET.get("company"))).first()

        except:
            city = None
            company = None

        # if not city or not company:
        #     return Response({'msg': 'city and company not found', 'status': 'failed'}, status=404)

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


class ServiceListAPIView(ListAPIView):
    serializer_class = HomeCareServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    pagination_class = CustomLimitPagination
    filter_backends = [
        DjangoFilterBackend,
    ]


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        company = request.user.company

        valid_companies = [company, ]

        category = request.GET.get("category")
        if category:
            category = get_object_or_404(Category, slug=uri_to_iri(category))
            child_categories = category.get_descendants()


            services = HomeCareService.objects.filter(is_active=True, is_deleted=False).filter(
                 Q(category_new=category) | Q(category_new__in=child_categories)
            )


            queryset = queryset.filter(service__in=services)

        is_active = request.GET.get("active")
        if is_active is not None:
            services = HomeCareService.objects.filter(is_active=is_active)
            queryset = queryset.filter(service__in=services)

        title = request.GET.get("search")
        if title:
            services = HomeCareService.objects.filter(title__icontains=title)
            queryset = queryset.filter(service__in=services)

        if not queryset.filter(company=company).exists():

            for obj in HomeCareCompany.objects.filter(is_plus=True, city=company.city):

                if (
                        HomeCareServicePrice.objects.filter(
                            service__in=services, city=company.city, company=obj
                        ).count()
                        > 0
                ):
                    valid_companies.append(obj)

        if company:
            queryset = queryset.filter(company__in=valid_companies)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class ServiceRetrieveAPIView(RetrieveAPIView):
    serializer_class = DetailServiceSerializer
    queryset = HomeCareServicePrice.objects.all()


class HomeCareCategoryListAPIViewV3(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.get_root_nodes()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        city = City.objects.filter(id=int(request.GET.get("city")))
        company = HomeCareCompany.objects.filter(id=int(request.GET.get("company")))
        if city.exists():
            if company.exists():
                city = City.objects.get(id=int(request.GET.get("city")))
                company = HomeCareCompany.objects.get(id=request.GET.get("company"))
                valid_categories = []
                for cat in queryset:
                    categories = cat.get_descendants()

                    services = HomeCareService.objects.filter(category_new__in=categories)

                    if (
                            HomeCareServicePrice.objects.filter(
                                service__in=services, city=city, company=company
                            ).count()
                            > 0
                    ):
                        valid_categories.append(cat)

                    for obj in HomeCareCompany.objects.filter(is_plus=True, city=city):

                        if (
                                HomeCareServicePrice.objects.filter(
                                    service__in=services, city=city, company=obj
                                ).count()
                                > 0 and cat not in valid_categories and not obj.allowed_categories in categories
                        ):
                            valid_categories.append(cat)

                serializer = self.get_serializer(valid_categories, many=True)
                return Response(serializer.data)
        else:
            return Response([])


class HomeCareSubCategoryListAPIViewV3(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        city_id = int(request.GET.get("city"))
        company = HomeCareCompany.objects.filter(id=int(request.GET.get("company")))
        if City.objects.filter(id=city_id).exists():
            city = City.objects.get(id=city_id)
            company = HomeCareCompany.objects.get(id=request.GET.get("company"))
            valid_categories = []
            exclude_ids = []
            category = get_object_or_404(
                Category, slug=uri_to_iri(kwargs.get("slug"))
            )
            queryset = category.get_children()
            for cat in queryset:
                categories = []
                categories.append(cat)
                cat_1 = cat.get_children()
                for c1 in cat_1:
                    categories.append(c1)
                    category_2 = c1.get_children()

                    for c2 in category_2:
                        categories.append(c2)
                        category_3 = c2.get_children()

                        for c3 in category_3:
                            categories.append(c3)
                            category_4 = c3.get_children()

                            for c4 in category_4:
                                categories.append(c4)


                services = HomeCareService.objects.filter(category_new__in=categories)

                if (
                        HomeCareServicePrice.objects.filter(
                            service__in=services, city=city, company=company
                        ).count()
                        > 0
                ):

                    exclude_ids.append(cat.id)
                    valid_categories.append(cat)

                for obj in HomeCareCompany.objects.filter(is_plus=True, city=city):

                    if (
                            HomeCareServicePrice.objects.filter(
                                service__in=services, city=city, company=obj
                            ).count()
                            > 0 and cat not in valid_categories
                    ):

                        valid_categories.append(cat)

            father = (
                CategorySerializer(category.get_parent()).data
                if category.get_parent()
                else None
            )
            category_data = CategorySerializer(category).data
            serializer = self.get_serializer(valid_categories, many=True)

            return Response(
                {"data": serializer.data, "category": category_data, "father": father}
            )
        else:
            return Response([])


class HomeCareServiceListAPIViewV3(ListAPIView):
    serializer_class = HomeCareServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    pagination_class = CustomLimitPagination
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "city",
    ]



    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        company = request.user.company

        valid_companies = [company, ]

        category = request.GET.get("category")
        if category:
            category = get_object_or_404(Category, slug=uri_to_iri(category))
            categories = category.get_descendants()


            services = HomeCareService.objects.filter(
                category_new__in=categories, is_active=True, is_deleted=False
            )

            queryset = queryset.filter(service__in=services)

        is_active = request.GET.get("active")
        if is_active is not None:
            services = HomeCareService.objects.filter(is_active=is_active)
            queryset = queryset.filter(service__in=services)

        title = request.GET.get("search")
        if title:
            services = HomeCareService.objects.filter(title__icontains=title)
            queryset = queryset.filter(service__in=services)

        if not queryset.filter(company=company).exists():

            for obj in HomeCareCompany.objects.filter(is_plus=True, city=company.city):

                if (
                        HomeCareServicePrice.objects.filter(
                            service__in=services, city=company.city, company=obj
                        ).count()
                        > 0
                ):
                    valid_companies.append(obj)

        if company:
            queryset = queryset.filter(company__in=valid_companies)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


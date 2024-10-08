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
)
from user.models import HomeCareCompany, CompanyManager, CityManager
from django.db.models import Q

class CityListAPIView(ListAPIView):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    pagination_class = CustomLimitPagination
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = ["province", "on_home"]


class ProvinceListAPIView(ListAPIView):
    serializer_class = ProvinceSerializer
    queryset = Province.objects.all()


class HomeCareServiceListAPIView(ListAPIView):
    serializer_class = HomeCareServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    pagination_class = CustomLimitPagination
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "city",
    ]

    # def get_user_company(self, user: User):
    #     register_code = user.register_code
    #     inviter_code = RegisterCode.objects.get(code=register_code)
    #     inviter_user = User.objects.filter(invite_code=inviter_code).last()
    #     if inviter_user:
    #         company = HomeCareCompany.objects.filter(user=inviter_user).last()
    #         return company
    #     return None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        company = request.user.company
        
        valid_companies = [company,]

        category = request.GET.get("category")
        if category:
            category = get_object_or_404(HomeCareCategory, slug=uri_to_iri(category))
            first_level_categories = HomeCareCategory.objects.filter(father=category)
            second_level_categories = HomeCareCategory.objects.filter(
                father__in=first_level_categories
            )
            third_level_categories = HomeCareCategory.objects.filter(
                father__in=second_level_categories
            )
            fourth_level_categories = HomeCareCategory.objects.filter(
                father__in=third_level_categories
            )
            fifth_level_categories = HomeCareCategory.objects.filter(
                father__in=fourth_level_categories
            )
            
            categories = [
                *first_level_categories,
                *second_level_categories,
                *third_level_categories,
                *fourth_level_categories,
                *fifth_level_categories,
                category,
            ]
            
            services = HomeCareService.objects.filter(
                category__in=categories, is_active=True, is_deleted=False
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
            
            for obj in HomeCareCompany.objects.filter(is_plus=True,city=company.city):
                
                if (
                HomeCareServicePrice.objects.filter(
                    service__in=services, city=company.city ,company=obj
                ).count()
                > 0 
                ) :
                    
                    valid_companies.append(obj)
            
        
        
        if company :
            queryset = queryset.filter(company__in=valid_companies)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
class HomeCareServiceRetrieveAPIView(RetrieveAPIView):
    serializer_class = DetailServiceSerializer
    queryset = HomeCareServicePrice.objects.all()


class HomeCareCategoryListAPIView(ListAPIView):
    serializer_class = HomeCareCategorySerializer
    queryset = HomeCareCategory.objects.filter(father=None)

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
                    first_level_categories = HomeCareCategory.objects.filter(father=cat)
                    second_level_categories = HomeCareCategory.objects.filter(
                        father__in=first_level_categories
                    )
                    third_level_categories = HomeCareCategory.objects.filter(
                        father__in=second_level_categories
                    )
                    fourth_level_categories = HomeCareCategory.objects.filter(
                        father__in=third_level_categories
                    )
                    fifth_level_categories = HomeCareCategory.objects.filter(
                        father__in=fourth_level_categories
                    )
                    categories = [
                        *first_level_categories,
                        *second_level_categories,
                        *third_level_categories,
                        *fourth_level_categories,
                        *fifth_level_categories,
                        cat,
                    ]
                    services = HomeCareService.objects.filter(category__in=categories)

                    if (
                        HomeCareServicePrice.objects.filter(
                            service__in=services, city=city, company=company
                        ).count()
                        > 0
                    ):
                        valid_categories.append(cat)
                    for obj in HomeCareCompany.objects.filter(is_plus=True,city=city):
                    
                        if (
                        HomeCareServicePrice.objects.filter(
                            service__in=services, city=city ,company=obj
                        ).count()
                        > 0 and cat not in valid_categories  and not obj.allowed_categories in categories
                        ):
                            valid_categories.append(cat)
            
                
                serializer = self.get_serializer(valid_categories, many=True)
                return Response(serializer.data)
        else:
            return Response([])


class HomeCareSubCategoryListAPIView(ListAPIView):
    serializer_class = HomeCareCategorySerializer
    queryset = HomeCareCategory.objects.all()

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
                HomeCareCategory, slug=uri_to_iri(kwargs.get("slug"))
            )
            queryset = queryset.filter(father=category)
            valid_categories_plus = []
            for cat in queryset:
                first_level_categories = HomeCareCategory.objects.filter(father=cat)
                second_level_categories = HomeCareCategory.objects.filter(
                    father__in=first_level_categories
                )
                third_level_categories = HomeCareCategory.objects.filter(
                    father__in=second_level_categories
                )
                fourth_level_categories = HomeCareCategory.objects.filter(
                    father__in=third_level_categories
                )
                categories = [
                    *first_level_categories,
                    *second_level_categories,
                    *third_level_categories,
                    *fourth_level_categories,
                    cat,
                ]
                
                services = HomeCareService.objects.filter(category__in=categories)
                
                if (
                    HomeCareServicePrice.objects.filter(
                        service__in=services, city=city ,company=company
                    ).count()
                    > 0
                ):
                    exclude_ids.append(cat.id)
                    valid_categories.append(cat)
             

                
                for obj in HomeCareCompany.objects.filter(is_plus=True,city=city):
                    
                    if (
                    HomeCareServicePrice.objects.filter(
                        service__in=services, city=city ,company=obj
                    ).count()
                    > 0 and cat not in valid_categories 
                    ):
                        valid_categories.append(cat)
            
                
            

            father = (
                HomeCareCategorySerializer(category.father).data
                if category.father
                else None
            )
            category_data = HomeCareCategorySerializer(category).data
            serializer = self.get_serializer(valid_categories, many=True)

            return Response(
                {"data": serializer.data, "category": category_data, "father": father}
            )
        else:
            return Response([])


class AddServicePriceAPIView(CreateAPIView):
    serializer_class = AddServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    permission_classes = (IsAuthenticated, IsManager, IsCityManager)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city = serializer.validated_data.get("city")
        service = serializer.validated_data.get("service")
        if HomeCareServicePrice.objects.filter(service=service, city=city,company=None).exists():
            return Response(
                {"msg": "برای این خدمت قیمت وجود دارد"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()


class ShortServiceListAPIView(ListAPIView):
    serializer_class = ShortServiceSerializer
    queryset = HomeCareService.objects.all()
    permission_classes = [IsAuthenticated, IsCityManager]

    def get_queryset(self):
        manager = CityManager.objects.get(user=self.request.user)
        city = manager.city

        allowed_categories = manager.allowed_categories.all()
        all_categories = list(allowed_categories)

        for category in allowed_categories:
            chain_category = None
            get_all = True
            while_count = 1
            if not category.father:
                for i in category.category_children.all():
                    if i in allowed_categories:
                        get_all = False
                if get_all:
                    all_categories.extend(get_all_child_categories(category))
            else:
                while while_count < HomeCareCategory.objects.count():
                    while_count += 1
                    if category in allowed_categories:
                        chain_category = category

                        for i in category.category_children.all():
                            if i in allowed_categories:
                                chain_category = category
                                while_count = 1000
                        if chain_category in allowed_categories:
                            break
                active_chain = True
                chain_two = False
                chain_three = False
                chain_four = False
                if chain_category:

                    for i in chain_category.category_children.all():
                        if i in allowed_categories:
                            active_chain = False
                    if active_chain:
                        chain_two = chain_category.category_children.all()
                        all_categories.extend(chain_two)
                if chain_two:

                    for x in chain_two:
                        all_categories.extend(x.category_children.all())
                        chain_three = x.category_children.all()
                if chain_three:
                    for x in chain_three:
                        all_categories.extend(x.category_children.all())
                        chain_four = x.category_children.all()
                if chain_four:
                    for x in chain_four:
                        all_categories.extend(x.category_children.all())

        queryset = HomeCareService.objects.filter(category__in=all_categories)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def get_all_child_categories(category):
    child_categories = HomeCareCategory.objects.filter(father=category)
    all_child_categories = list(child_categories)
    for child_category in child_categories:
        all_child_categories.extend(get_all_child_categories(child_category))
    return all_child_categories

class ServicePriceRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AddServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    permission_classes = (IsAuthenticated, IsManager, IsCityManager)

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")


class ShortServicePriceListAPIView(ListAPIView):
    serializer_class = ShortServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    permission_classes = (IsAuthenticated, IsManager, IsCityManager)

    def list(self, request, *args, **kwargs):
        city_manager = CityManager.objects.get(user=self.request.user)
        allowed_categories = city_manager.allowed_categories.all()

        queryset = self.filter_queryset(self.get_queryset())
        cities = request.user.manager.city.all()

        queryset = queryset.filter(
            city__in=cities,company=None
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CompanyAddServicePriceAPIView(CreateAPIView):
    serializer_class = AddServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    permission_classes = (IsAuthenticated, IsCompanyManager)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city = serializer.validated_data.get("city")
        company = serializer.validated_data.get("company")
        service = serializer.validated_data.get("service")
        if HomeCareServicePrice.objects.filter(
            service=service,city=city,company=company
        ).exists():
            return Response(
                {"msg": "برای این خدمت قیمت وجود دارد"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()


class CompanyShortServiceListAPIView(ListAPIView):
    serializer_class = ShortServiceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        
            company_manager = CompanyManager.objects.get(user=self.request.user)
            company = company_manager.company
            allowed_categories = company.allowed_categories.all()
            all_categories = list(allowed_categories)

            for category in allowed_categories:
                chain_category = None
                get_all = True
                while_count = 1
                if not category.father:
                    for i in category.category_children.all():
                        if i in allowed_categories:
                            get_all = False
                    if get_all:
                        all_categories.extend(get_all_child_categories(category))
                else:
                    while while_count < HomeCareCategory.objects.count():
                        while_count += 1
                        if category in allowed_categories:
                            chain_category = category
                            
                            for i in category.category_children.all():
                                if i in allowed_categories:
                                    chain_category = category
                                    while_count = 1000
                            if chain_category in allowed_categories:
                                break
                    active_chain = True
                    chain_two= False
                    chain_three = False
                    chain_four = False
                    if chain_category:
                        
                        for i in chain_category.category_children.all():
                            if i in allowed_categories:
                                active_chain = False
                        if active_chain:
                            chain_two = chain_category.category_children.all()
                            all_categories.extend(chain_two)
                    if chain_two:
                        
                        for x in chain_two:
                            all_categories.extend(x.category_children.all())
                            chain_three = x.category_children.all()
                    if chain_three:
                        for x in chain_three:
                            all_categories.extend(x.category_children.all())
                            chain_four = x.category_children.all()
                    if chain_four:
                        for x in chain_four:
                            all_categories.extend(x.category_children.all())

                            
                                
                            
            queryset = HomeCareService.objects.filter(category__in=all_categories)
            return queryset
    

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def get_all_child_categories(category):
    child_categories = HomeCareCategory.objects.filter(father=category)
    all_child_categories = list(child_categories)
    for child_category in child_categories:
        all_child_categories.extend(get_all_child_categories(child_category))
    return all_child_categories

    
class CompanyServicePriceRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AddServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    permission_classes = (IsAuthenticated, IsCompanyManager)

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")


class CompanyShortServicePriceListAPIView(ListAPIView):
    serializer_class = ShortServicePriceSerializer
    queryset = HomeCareServicePrice.objects.all()
    permission_classes = (IsAuthenticated, IsCompanyManager)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # cities = request.user.manager.city.all()
        city = request.user.company_manager.company.city
        company = request.user.company_manager.company
        # services = request.user.manager.services.all()
        # queryset = queryset.filter(city__in=cities, service__in=services)
        queryset = queryset.filter(city=city, company=company)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class CategoryAjaxSearchApi(APIView):
    def get(self, request):
        categories = HomeCareCategory.objects.all()

        search_param = request.GET.get('q', None)
        if search_param:
            categories = categories.filter(title__icontains=search_param)


        data = CategorySearchSerializer(categories, many=True).data
        return Response({"query": search_param,"results": data})


class ServiceAjaxSearchApi(APIView):
    def get(self, request):
        services = HomeCareService.objects.all()

        search_param = request.GET.get('q', None)
        if search_param:
            services = services.filter(title__icontains=search_param)


        data = ServicesSearchSerializer(services, many=True).data
        return Response({"query": search_param,"results": data})


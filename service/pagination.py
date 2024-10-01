from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
from rest_framework.response import Response
from django.utils.encoding import force_str
class DefaultPagination(LimitOffsetPagination):
    page_size = 12
    default_limit = 12

    def get_paginated_response(self, data):
        page_count = (self.count // self.limit) if (self.count % self.limit == 0) else (self.count // self.limit) + 1
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_count': int(page_count),
            'count': self.count,
            'results': data
        })
    
class MyPagination(PageNumberPagination):
    page_size = 12
    def get_paginated_response(self, data):
        count = self.page.paginator.count
        page_count = self.page.paginator.num_pages
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_count': page_count if count > 0 else 0 ,
            'count': count,
            'results': data
        })
    
class CustomLimitPagination(PageNumberPagination):
    page_size = 18
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 10000

    def get_paginated_response(self, data):
        count = self.page.paginator.count
        page_count = self.page.paginator.num_pages
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'limit': self.get_page_size(self.request),
            'page_count': page_count if count > 0 else 0 ,
            'count': count,
            'results': data
        })
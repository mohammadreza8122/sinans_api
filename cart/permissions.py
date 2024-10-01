from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "manager")


class IsCityManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.city in request.user.manager.city.all()

class IsCompanyManager(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "company_manager")
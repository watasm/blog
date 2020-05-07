from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import IsAuthenticated

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user

class IsAdminUserOrReadOnly(IsAdminUser):
    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin

class IsUserOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'list' and not request.user.is_superuser:
            return False
        else:
            return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj or request.user.is_superuser

class IsOwnerOrAdminUser(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'list' and not request.user.is_superuser:
            return False
        else:
            return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_superuser

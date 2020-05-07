from rest_framework.permissions import BasePermission

class IsInGroupOrAdminPermission(BasePermission):
    # if returned all groups
    # def has_permission(self, request, view):
    #     if view.action == 'list' and not request.user.is_superuser:
    #         return False
    #     else:
    #         return True

    def has_object_permission(self, request, view, obj):
        if request.user in obj.participants.all() or request.user.is_superuser:
            return True
        return False

from rest_framework import permissions


class IsOwnerOrReadonly(permissions.BasePermission):
    """This class creates permissions for delete and update methods"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

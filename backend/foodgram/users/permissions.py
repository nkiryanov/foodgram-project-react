from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS

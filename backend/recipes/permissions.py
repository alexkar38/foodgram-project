from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return (
                    request.user.is_staff
                    or request.user == obj.author
                    or request.user.is_superuser
                )
        return request.user.is_authenticated
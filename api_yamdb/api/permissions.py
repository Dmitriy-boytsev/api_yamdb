from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.is_superuser
                     or request.user.role == User.RoleChoices.ADMIN))


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.is_superuser
                         or request.user.role
                         == User.RoleChoices.ADMIN)))


class IsAdminAuthorModeratorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.role == User.RoleChoices.ADMIN
                or request.user.role == User.RoleChoices.MODERATOR
                or obj.author == request.user
                )

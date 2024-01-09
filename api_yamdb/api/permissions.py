from django.contrib.auth import get_user_model
from rest_framework import permissions


User = get_user_model()


class IsAdminOnly(permissions.BasePermission):
    """Право доступа только для администратора."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Право доступа администратора. Иначе доступно для чтения."""

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_admin)


class IsAdminAuthorModeratorOrReadOnly(permissions.BasePermission):
    """Право доступа администратора, модератора, автора. Иначе доступно для чтения."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user
                )

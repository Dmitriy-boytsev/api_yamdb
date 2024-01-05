from django.contrib.auth import get_user_model
from rest_framework import permissions

from reviews.models import CustomUser
User = get_user_model()
#

class AdminSignupPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and view.basename == 'user':
            email = request.data.get('email', None)
            if email and CustomUser.objects.filter(email=email).exists():
                return False

        return (request.user.is_authenticated
                and (request.user.is_superuser
                     or request.user.role == CustomUser.RoleChoices.ADMIN))

    def has_object_permission(self, request, view, obj):
        return True


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.is_superuser
                         or request.user.role
                         == CustomUser.RoleChoices.ADMIN)))


class IsAdminAuthorModeratorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.role == CustomUser.RoleChoices.ADMIN
                or request.user.role == CustomUser.RoleChoices.MODERATOR
                or obj.author == request.user
                )

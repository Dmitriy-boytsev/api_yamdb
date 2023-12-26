from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, get_jwt_token, signup, user_profile

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet)


auth_path = [
    path('auth/signup/', signup, name='signup),
    path('auth/token/', get_jwt_token, name='get_jwt_token'),
]

urlpatterns = [
    path('v1/users/me/', user_profile, name='user_profile'),
    path('v1/', include(router_v1.urls)),
    path('v1/', include(auth_path)),
]

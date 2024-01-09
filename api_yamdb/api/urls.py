from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet,
    ReviewViewSet, TitleViewSet, UserViewSet,
    get_jwt_token, signup
)

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
v1_router.register(
    'users',
    UserViewSet,
    basename='users'
)
v1_router.register(
    'categories',
    CategoryViewSet,
    basename='сategories'
)
v1_router.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
v1_router.register(
    'genres',
    GenreViewSet,
    basename='genres'
)

auth_path = [
    path('token/', get_jwt_token, name='get_jwt_token'),
    path('signup/', signup, name='signup'),
]

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/', include(auth_path)),
]

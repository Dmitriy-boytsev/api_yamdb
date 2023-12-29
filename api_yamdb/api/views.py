from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.api.mixins import CreateListDestroyViewSet
from api_yamdb.api.permissions import IsAdminAuthorModeratorOrReadOnly, IsAdminOrReadOnly
from api_yamdb.api.permissions import IsAdminOnly
from api_yamdb.api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleCreateSerializer, TitleReadSerializer
)
from api_yamdb.api.serializers import SignUpSerializer, TokenSerializer, UserSerializer
from api_yamdb.reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Регистрация нового пользователя."""
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email,
            )
        except IntegrityError:
            return Response(
                'Нельзя использовать данный электронный адрес!',
                status=status.HTTP_400_BAD_REQUEST,
            )

        confirm_code = default_token_generator.make_token(user)
        send_mail(
            subject='Получение кода подтверждения',
            message=f'Ваш код подтверждения: {confirm_code}.',
            from_email=settings.EMAIL_ADMIN,
            recipient_list=[user.email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """Получение JWT-токена."""
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        confirm_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)

        if default_token_generator.check_token(user, confirm_code):
            token = AccessToken.for_user(user)
            return Response({'token': token}, status=status.HTTP_200_OK)
        return Response(
            'Ошибка получения кода подтверждения. Попробуйте еще раз.',
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
def user_profile(request):
    """Персональная страница пользователя."""
    current_user = request.user
    if request.method == 'PATCH':
        serializer = UserSerializer(
            current_user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=current_user.role)
    serializer = UserSerializer(current_user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    """Вьюсет для работы с моделью User."""

    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewSet):
    """Вьюсет категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """Вьюсет жанра."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет произведения."""

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateSerializer


class BaseCommentReviewViewSet(viewsets.ModelViewSet):
    serializer_class = None
    model_class = None
    permission_classes = (IsAdminAuthorModeratorOrReadOnly,)

    def get_queryset(self):
        instance = get_object_or_404(
            self.model_class,
            id=self.kwargs.get(f'{self.model_class.__name__.lower()}_id')
        )
        return instance.comments.all()

    def perform_create(self, serializer):
        instance = get_object_or_404(
            self.model_class,
            id=self.kwargs.get(f'{self.model_class.__name__.lower()}_id')
        )
        serializer.save(
            author=self.request.user,
            **{f'{self.model_class.__name__.lower()}': instance}
        )


class CommentViewSet(BaseCommentReviewViewSet):
    serializer_class = CommentSerializer
    model_class = Comment


class ReviewViewSet(BaseCommentReviewViewSet):
    serializer_class = ReviewSerializer
    model_class = Review

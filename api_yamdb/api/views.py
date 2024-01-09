from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Review, Title

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.mixins import CreateListDestroyViewSet
from api.permissions import (
    IsAdminAuthorModeratorOrReadOnly, IsAdminOnly, IsAdminOrReadOnly
)
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, SignUpSerializer, TitleCreateSerializer,
    TitleReadSerializer, TokenSerializer, UserSerializer
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Регистрация нового пользователя."""

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, _ = User.objects.get_or_create(
            username=username,
            email=email,
        )

        confirm_code = default_token_generator.make_token(user)
        send_mail(
            subject='Получение кода подтверждения',
            message=f'Ваш код подтверждения: {confirm_code}.',
            from_email=settings.EMAIL_ADMIN,
            recipient_list=[user.email], )
        return Response(serializer.data, status=status.HTTP_200_OK)

    except IntegrityError:
        return Response(
            'Нельзя использовать данный электронный адрес!',
            status=status.HTTP_400_BAD_REQUEST, )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """Получение JWT-токена."""

    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirm_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)

    if default_token_generator.check_token(user, confirm_code):
        token = str(AccessToken.for_user(user))
        return Response({'token': token}, status=status.HTTP_200_OK)
    return Response(
        'Ошибка получения кода подтверждения. Попробуйте еще раз.',
        status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PATCH'])
# def user_profile(request):
#     """Персональная страница пользователя."""
#
#     current_user = request.user
#     if request.method == 'PATCH':
#         serializer = UserSerializer(
#             current_user,
#             data=request.data,
#             partial=True,
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save(role=current_user.role)
#     serializer = UserSerializer(current_user)
#     return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    """Вьюсет для работы с моделью User."""

    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        url_path='me')
    def user_profile(self, request):
        """Редактирование собственной страницы."""

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


class CategoryViewSet(CreateListDestroyViewSet):
    """Вьюсет категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    """Вьюсет жанра."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет произведения."""

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']

    def get_queryset(self):
        return Title.objects.all().annotate(rating=Avg('reviews__score'))

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет отзыва."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminAuthorModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет комментария."""

    serializer_class = CommentSerializer
    permission_classes = (IsAdminAuthorModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']

    def get_title_and_review(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        review = get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title=title
        )
        return title, review

    def get_queryset(self):
        _, review = self.get_title_and_review()
        return review.comments.all()

    def perform_create(self, serializer):
        title, review = self.get_title_and_review()
        serializer.save(author=self.request.user, review=review)

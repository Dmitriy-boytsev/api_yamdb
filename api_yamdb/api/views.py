from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.permissions import IsAdminAuthorModeratorOrReadOnly, IsAdminOrReadOnly
from api.mixins import CreateListDestroyViewSet
from api_yamdb.api.serializers import SignUpSerializer
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleCreateSerializer, TitleReadSerializer
)
from reviews.models import Category, Comment, Genre, Review, Title



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

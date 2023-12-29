from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.mixins import CreateListDestroyViewSet
from api.permissions import IsAdminAuthorModeratorOrReadOnly, IsAdminOrReadOnly
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleCreateSerializer, TitleReadSerializer
)
from reviews.models import Category, Comment, Genre, Review, Title


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

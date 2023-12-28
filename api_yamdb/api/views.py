from rest_framework import viewsets
from django.shortcuts import get_object_or_404

from reviews.models import Review, Comment
from .serializers import CommentSerializer, ReviewSerializer
from .permissions import IsAdminAuthorModeratorOrReadOnly


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

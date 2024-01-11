from django.contrib.auth import get_user_model
from django.db import models

from reviews.constants import (
    LIMIT_CATEGORY_GENRE_NAME, TITLE_LIMIT
)

User = get_user_model()


class BaseModelReviewsComment(models.Model):
    """Абстрактная модель для комментариев и отзывов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата', auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Текст: {self.text} . Автора: {self.author}'


class BaseModelCategoryGenre(models.Model):
    """Абстрактная модель для категорий и жанров."""

    name = models.CharField(
        'Заголовок',
        max_length=LIMIT_CATEGORY_GENRE_NAME
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:TITLE_LIMIT]

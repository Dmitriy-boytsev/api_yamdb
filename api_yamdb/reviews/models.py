from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year


User = get_user_model()
TITLE_LIMIT = 30


class Category(models.Model):
    """Модель категории."""

    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Идентификатор', unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:TITLE_LIMIT]


class Genre(models.Model):
    """Модель жанра."""

    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Идентификатор', unique=True)

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.title[:TITLE_LIMIT]


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField('Название произведения', max_length=200)
    year = models.IntegerField('Год выхода', validators=(validate_year,))
    description = models.TextField('Описание')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        null=True
    )
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:TITLE_LIMIT]


class Review(models.Model):
    """Модель отзыва."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Заголовок отзыва'
    )
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    score = models.PositiveSmallIntegerField(
        'Оценка произведения',
        validators=[
            MinValueValidator(1, message='Оценка должна быть от 1'),
            MaxValueValidator(10, message='Оценка должна быть до 10')
        ]
    )

    class Meta:
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Текст отзыва: {self.text} . Автора: {self.author}'


class Comment(models.Model):
    """Модель комментария."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Комментарий к отзыву'
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField('Дата комментария', auto_now_add=True)

    class Meta:
        default_related_name = 'comments'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Текст комментария: {self.text} . Автора: {self.author}'

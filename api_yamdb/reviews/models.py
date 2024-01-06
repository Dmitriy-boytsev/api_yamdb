from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from reviews.constants import (LIMIT_USERNAME_LENGTH,
                               LIMIT_USER_EMAIL_LENGTH,
                               LIMIT_USER_ROLE_LENTGH,
                               LIMIT_NAME_LENGHT)
from reviews.validators import validate_year

TITLE_LIMIT = 30


class CustomUser(AbstractUser):
    class RoleChoices(models.TextChoices):
        USER = 'user'
        ADMIN = 'admin'
        MODERATOR = 'moderator'

    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=LIMIT_USERNAME_LENGTH
    )
    email = models.EmailField(
        'Email',
        unique=True,
        max_length=LIMIT_USER_EMAIL_LENGTH
    )
    role = models.CharField(
        'Роль',
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
        max_length=LIMIT_USER_ROLE_LENTGH
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    first_name = models.CharField(
        'Имя', blank=True,
        max_length=LIMIT_NAME_LENGHT
    )
    last_name = models.CharField(
        'Фамилия',
        blank=True,
        max_length=LIMIT_NAME_LENGHT
    )

    @property
    def is_admin(self):
        """Пользователь имеет права администратора."""
        return (
                self.role == self.RoleChoices.ADMIN
                or self.is_superuser
        )

    @property
    def is_moderator(self):
        """Пользователь имеет права модератора."""
        return (
                self.role == self.RoleChoices.MODERATOR
                or self.is_staff
        )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username} ({self.role})'


class Category(models.Model):
    """Модель категории."""

    name = models.CharField(
        'Заголовок',
        max_length=200
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:TITLE_LIMIT]


class Genre(models.Model):
    """Модель жанра."""

    name = models.CharField(
        'Заголовок',
        max_length=200
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:TITLE_LIMIT]


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        'Название произведения',
        max_length=200
    )
    year = models.IntegerField(
        'Год выхода',
        validators=(validate_year,)
    )
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
        CustomUser,
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
        unique_together = ('author', 'title')
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Текст отзыва: {self.text} . Автора: {self.author}'


class Comment(models.Model):
    """Модель комментария."""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Комментарий к отзыву'
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField(
        'Дата комментария', auto_now_add=True
    )

    class Meta:
        default_related_name = 'comments'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Текст комментария: {self.text} . Автора: {self.author}'

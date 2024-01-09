from django.contrib.auth.models import AbstractUser
from django.db import models

from reviews.constants import (LIMIT_USERNAME_LENGTH,
                               LIMIT_USER_EMAIL_LENGTH,
                               LIMIT_USER_ROLE_LENTGH,
                               LIMIT_NAME_LENGHT)


class User(AbstractUser):
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

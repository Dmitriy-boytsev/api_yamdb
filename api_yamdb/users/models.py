from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class RoleChoices(models.TextChoices):
        USER = 'user'
        ADMIN = 'admin'
        MODERATOR = 'moderator'

    username = models.CharField('Имя пользователя', unique=True, max_length=100)
    email = models.EmailField('Email', unique=True, max_length=150)
    role = models.CharField('Роль', choices=RoleChoices.choices, default=RoleChoices.USER, )
    bio = models.TextField('Биография', blank=True, )
    first_name = models.CharField('Имя', blank=True, max_length=100)
    last_name = models.CharField('Фамилия', blank=True, max_length=100)

    def __str__(self):
        return self.username

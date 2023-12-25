from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        USER = 'user'
        ADMIN = 'admin'
        MODERATOR = 'moderator'

    username = models.CharField('Имя пользователя', unique=True, blank=False, null=False, )
    email = models.EmailField('Email', unique=True, blank=False, null=False, )
    role = models.CharField('Роль', choices=RoleChoices.choices, default=RoleChoices.USER, )
    bio = models.TextField('Биография', blank=True, )
    first_name = models.CharField('Имя', blank=True, )
    last_name = models.CharField('Фамилия', blank=True)

    def __str__(self):
        return self.username

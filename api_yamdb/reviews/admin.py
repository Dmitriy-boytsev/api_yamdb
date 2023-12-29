from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import CustomUser

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio',)}),
)
admin.site.register(CustomUser, UserAdmin)

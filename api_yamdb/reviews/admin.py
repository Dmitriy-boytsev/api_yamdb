from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title


class BaseModelAdmin(admin.ModelAdmin):
    empty_value_display = 'Отсутствует'
    ordering = ['id']


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Genre)
class GenreAdmin(BaseModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Title)
class TitleAdmin(BaseModelAdmin):
    list_display = ('name', 'year', 'category', 'description')
    search_fields = ('name',)
    list_filter = ('name', 'category', 'year')


@admin.register(GenreTitle)
class GenreTitleAdmin(BaseModelAdmin):
    """Класс настройки соответствия жанров и произведений."""

    list_display = ('genre', 'title')
    list_filter = ('genre',)
    search_fields = ('title',)


@admin.register(Review)
class ReviewAdmin(BaseModelAdmin):
    list_display = ('title', 'text', 'author', 'score')
    search_fields = ('pub_date',)
    list_filter = ('pub_date',)


@admin.register(Comment)
class CommentAdmin(BaseModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    search_fields = ('review',)
    list_filter = ('review',)

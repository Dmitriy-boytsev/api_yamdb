from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class BaseModelAdmin(admin.ModelAdmin):
    empty_value_display = 'Отсутствует'
    ordering = ('id',)


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Comment)
class CommentAdmin(BaseModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    search_fields = ('review',)
    list_filter = ('review',)


@admin.register(Genre)
class GenreAdmin(BaseModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Review)
class ReviewAdmin(BaseModelAdmin):
    list_display = ('title', 'text', 'author', 'score')
    search_fields = ('pub_date',)
    list_filter = ('pub_date',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'description', 'genres_list')
    search_fields = ('name',)
    list_filter = ('name', 'category', 'year')
    list_editable = ('category',)

    def genres_list(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])
    genres_list.short_description = 'Genres'

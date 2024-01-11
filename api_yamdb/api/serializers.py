from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.constants import (LIMIT_USERNAME_LENGTH,
                               LIMIT_USER_EMAIL_LENGTH)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категерии."""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведения."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Title
        fields = '__all__'


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведения."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, title):
        serializer = TitleReadSerializer(title)
        return serializer.data


class SignUpSerializer(serializers.Serializer):
    """Регистрация нового пользователя."""

    username = serializers.RegexField(
        required=True,
        regex=r'^[\w.@+-]+\Z',
        max_length=LIMIT_USERNAME_LENGTH
    )
    email = serializers.EmailField(
        required=True, max_length=LIMIT_USER_EMAIL_LENGTH
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве имени пользователя'
            )
        return value


class TokenSerializer(serializers.Serializer):
    """Получение JWT-токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True, max_length=LIMIT_USERNAME_LENGTH,
        validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(
        required=True,
        max_length=LIMIT_USER_EMAIL_LENGTH,
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве имени пользователя'
            )
        if User.objects.filter(username=value).exists():
            return serializers.ValidationError(
                'Данное имя пользователя уже существует')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            return serializers.ValidationError(
                'Данный Email уже зарегистрирован')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        model = Review
        fields = (
            'id', 'text', 'author', 'score', 'pub_date'
        )

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                'Оценка должна быть от 1 до 10'
            )
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        if request.method == 'POST' and Review.objects.filter(
            title_id=self.context.get('view').kwargs.get('title_id'),
            author=author
        ).exists():
            raise ValidationError('Может быть не более одного отзыва!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')

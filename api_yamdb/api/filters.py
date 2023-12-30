import django_filters as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug')
    year = filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = '__all__'

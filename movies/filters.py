import django_filters
from django.db.models import Q

from .models import Movie


class MovieFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(
        method="filter_search"
    )

    director_id = django_filters.NumberFilter(
        field_name="director_id"
    )

    genre_id = django_filters.NumberFilter(
        field_name="genres__id"
    )

    year = django_filters.NumberFilter(
        field_name="year"
    )

    sort_by = django_filters.OrderingFilter(
        fields=(
            ("title", "title"),
            ("year", "year"),
            ("rating", "rating"),
            ("duration_min", "duration_min"),
            ("country", "country"),
        )
    )

    class Meta:
        model = Movie
        fields = [
            "director_id",
            "genre_id",
            "year",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value)
            | Q(description__icontains=value)
            | Q(country__icontains=value)
        )

from rest_framework import serializers
from .models import Movie, Director, Genre


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ["id", "name", "bio", "birth_date", "country",]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class MovieSerializer(serializers.ModelSerializer):
    director_name = serializers.CharField(
        source="director.name",
        read_only=True,
    )
    genre_names = serializers.StringRelatedField(
        source="genres",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "year",
            "duration_min",
            "country",
            "rating",
            "director",
            "director_name",
            "genres",
            "genre_names",
        ]

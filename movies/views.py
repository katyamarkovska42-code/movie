from django.shortcuts import get_object_or_404
from django.db.models import ProtectedError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from movies.permissions import IsOwnerOrAdmin

from .models import Movie, Director, Genre
from .serializers import (
    MovieSerializer,
    DirectorSerializer,
    GenreSerializer,
)
from .filters import MovieFilter
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiTypes,
)


import logging

logger = logging.getLogger(__name__)


class MovieListCreateView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search movies by title, description or country."
            ),
            OpenApiParameter(
                name="director_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter movies by director ID."
            ),
            OpenApiParameter(
                name="genre_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter movies by genre ID."
            ),
            OpenApiParameter(
                name="year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter movies by release year."
            ),
            OpenApiParameter(
                name="sort_by",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Sort movies by title, year, rating, "
                    "duration_min or country. "
                    "Use a minus sign for descending order."
                )
            ),
        ],
        responses=MovieSerializer(many=True),
        description="Retrieve a list of movies with filtering and sorting."
    )
    def get(self, request):
        movies = Movie.objects.all()

        movie_filter = MovieFilter(
            request.query_params,
            queryset=movies
        )

        movies = movie_filter.qs.distinct()

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=MovieSerializer,
        responses={
            201: MovieSerializer,
            400: OpenApiResponse(
                description="Invalid input data."
            ),
        },
        description="Create a new movie. Authentication is required."
    )
    def post(self, request):
        serializer = MovieSerializer(data=request.data)

        if serializer.is_valid():
            movie = serializer.save(owner=request.user)
            logger.info("Movie created: ID %s", movie.id)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class MovieDetailView(APIView):

    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrAdmin
    ]

    @extend_schema(
        responses=MovieSerializer,
        description="Retrieve a movie by its ID."
    )
    def get(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        self.check_object_permissions(request, movie)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    @extend_schema(
        request=MovieSerializer,
        responses={
            200: MovieSerializer,
            400: OpenApiResponse(
                description="Invalid input data."
            ),
        },
        description="Update a movie by its ID."
    )
    def put(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        self.check_object_permissions(request, movie)
        serializer = MovieSerializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            logger.info("Movie updated: ID %s", movie.id)
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        responses={
            204: OpenApiResponse(
                description="Movie deleted successfully."
            ),
        },
        description="Delete a movie by its ID. Only the owner or an admin can delete it."
    )
    def delete(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        self.check_object_permissions(request, movie)
        movie.delete()
        logger.info("Movie deleted: ID %s", pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PopularMoviesView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        responses=MovieSerializer(many=True),
        description="Retrieve movies sorted by rating in descending order."
    )
    def get(self, request):
        movies = Movie.objects.filter(
            rating__isnull=False
        ).order_by("-rating", "-year")

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)



class DirectorListCreateView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        responses=DirectorSerializer(many=True),
        description="Retrieve a list of directors."
    )
    def get(self, request):
        directors = Director.objects.all().order_by("name")
        serializer = DirectorSerializer(directors, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=DirectorSerializer,
        responses={
            201: DirectorSerializer,
            400: OpenApiResponse(
                description="Invalid input data."
            ),
        },
        description="Create a new director."
    )
    def post(self, request):
        serializer = DirectorSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class DirectorDetailView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        responses=DirectorSerializer,
        description="Retrieve a director by its ID."
    )
    def get(self, request, pk):
        director = get_object_or_404(Director, pk=pk)
        serializer = DirectorSerializer(director)
        return Response(serializer.data)

    @extend_schema(
        request=DirectorSerializer,
        responses={
            200: DirectorSerializer,
            400: OpenApiResponse(
                description="Invalid input data."
            ),
        },
        description="Update a director by its ID."
    )
    def put(self, request, pk):
        director = get_object_or_404(Director, pk=pk)
        serializer = DirectorSerializer(director, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        responses={
            204: OpenApiResponse(
                description="Director deleted successfully."
            ),
            409: OpenApiResponse(
                description="Cannot delete a director who has movies."
            ),
        },
        description="Delete a director by its ID."
    )
    def delete(self, request, pk):
        director = get_object_or_404(Director, pk=pk)

        try:
            director.delete()
        except ProtectedError:
            return Response(
                {"error": "Не можна видалити режисера, який має фільми."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)



class GenreListCreateView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        responses=GenreSerializer(many=True),
        description="Retrieve a list of genres."
    )
    def get(self, request):
        genres = Genre.objects.all().order_by("name")
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=GenreSerializer,
        responses={
            201: GenreSerializer,
            400: OpenApiResponse(
                description="Invalid input data."
            ),
        },
        description="Create a new genre."
    )
    def post(self, request):
        serializer = GenreSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class GenreDetailView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        responses=GenreSerializer,
        description="Retrieve a genre by its ID."
    )
    def get(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        serializer = GenreSerializer(genre)
        return Response(serializer.data)

    @extend_schema(
        request=GenreSerializer,
        responses={
            200: GenreSerializer,
            400: OpenApiResponse(
                description="Invalid input data."
            ),
        },
        description="Update a genre by its ID."
    )
    def put(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        serializer = GenreSerializer(genre, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        responses={
            204: OpenApiResponse(
                description="Genre deleted successfully."
            ),
        },
        description="Delete a genre by its ID."
    )
    def delete(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreMoviesView(APIView):

    @extend_schema(
        responses=MovieSerializer(many=True),
        description="Retrieve all movies belonging to a specific genre."
    )
    def get(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        movies = Movie.objects.filter(genres=genre).order_by("-year")

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

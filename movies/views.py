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


class MovieListCreateView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        movies = Movie.objects.all()

        movie_filter = MovieFilter(
            request.query_params,
            queryset=movies
        )

        movies = movie_filter.qs.distinct()

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.user)
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

    def get(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        self.check_object_permissions(request, movie)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        self.check_object_permissions(request, movie)
        serializer = MovieSerializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        self.check_object_permissions(request, movie)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PopularMoviesView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        movies = Movie.objects.filter(
            rating__isnull=False
        ).order_by("-rating", "-year")

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)



class DirectorListCreateView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        directors = Director.objects.all().order_by("name")
        serializer = DirectorSerializer(directors, many=True)
        return Response(serializer.data)

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

    def get(self, request, pk):
        director = get_object_or_404(Director, pk=pk)
        serializer = DirectorSerializer(director)
        return Response(serializer.data)

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

    def get(self, request):
        genres = Genre.objects.all().order_by("name")
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

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

    def get(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        serializer = GenreSerializer(genre)
        return Response(serializer.data)

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

    def delete(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreMoviesView(APIView):

    def get(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        movies = Movie.objects.filter(genres=genre).order_by("-year")

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

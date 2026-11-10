
from django.urls import path

from .views import (
    DirectorDetailView,
    DirectorListCreateView,
    GenreDetailView,
    GenreListCreateView,
    GenreMoviesView,
    MovieDetailView,
    MovieListCreateView,
    PopularMoviesView,
)

urlpatterns = [
    path("movies/", MovieListCreateView.as_view(), name="movie-list"),
    path("movies/popular/", PopularMoviesView.as_view(), name="movie-popular"),
    path("movies/<int:pk>/", MovieDetailView.as_view(), name="movie-detail"),

    path("directors/", DirectorListCreateView.as_view(), name="director-list"),
    path(
        "directors/<int:pk>/",
        DirectorDetailView.as_view(),
        name="director-detail",
    ),

    path("genres/", GenreListCreateView.as_view(), name="genre-list"),
    path("genres/<int:pk>/", GenreDetailView.as_view(), name="genre-detail"),
    path(
        "genres/<int:pk>/movies/",
        GenreMoviesView.as_view(),
        name="genre-movies",
    ),
]

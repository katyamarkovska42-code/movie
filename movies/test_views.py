import pytest
from django.urls import reverse
from movies.models import Movie


@pytest.mark.django_db
def test_create_movie_valid_token(api_client, user, director) -> None:
    """
    Test creating a movie with a valid JWT token.
    """
    login_url = reverse("token-obtain-pair")

    token_response = api_client.post(
        login_url,
        {
            "username": "testuser",
            "password": "testpassword123"
        },
        format="json"
    )

    assert token_response.status_code == 200

    access_token = token_response.data["access"]

    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access_token}"
    )

    response = api_client.post(
        "/api/movies/",
        {
            "title": "Inception",
            "description": "A science fiction film",
            "year": 2010,
            "duration_min": 148,
            "country": "USA",
            "rating": 8.8,
            "director": director.id,
            "genres": []
        },
        format="json"
    )

    assert response.status_code == 201
    assert Movie.objects.filter(title="Inception").exists()


@pytest.mark.django_db
def test_get_movie_list(api_client, movie) -> None:
    """
    Test retrieving a list of movies.
    """
    response = api_client.get("/api/movies/", format="json")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Interstellar"


@pytest.mark.django_db
def test_get_movie_empty_list(api_client) -> None:
    """
    Test retrieving an empty list of movies.
    """
    response = api_client.get("/api/movies/", format="json")

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_get_movie_detail(api_client, movie) -> None:
    """
    Test retrieving a movie by ID.
    """
    response = api_client.get(
        f"/api/movies/{movie.id}/",
        format="json"
    )

    assert response.status_code == 200
    assert response.data["title"] == "Interstellar"


@pytest.mark.django_db
def test_get_movie_detail_not_found(api_client) -> None:
    """
    Test retrieving a movie that does not exist.
    """
    response = api_client.get("/api/movies/9999/", format="json")

    assert response.status_code == 404


@pytest.mark.django_db
def test_create_movie(authenticated_client, director) -> None:
    """
    Test creating a movie by an authenticated user.
    """
    data = {
        "title": "Inception",
        "description": "A science fiction film",
        "year": 2010,
        "duration_min": 148,
        "country": "USA",
        "rating": 8.8,
        "director": director.id,
        "genres": []
    }

    response = authenticated_client.post(
        "/api/movies/",
        data,
        format="json"
    )

    assert response.status_code == 201
    assert Movie.objects.filter(title="Inception").exists()


@pytest.mark.django_db
def test_create_movie_unauthorized(api_client, director) -> None:
    """
    Test that an unauthenticated user cannot create a movie.
    """
    data = {
        "title": "Inception",
        "year": 2010,
        "director": director.id,
        "genres": []
    }

    response = api_client.post(
        "/api/movies/",
        data,
        format="json"
    )

    assert response.status_code == 401
    assert Movie.objects.count() == 0


@pytest.mark.django_db
def test_create_movie_invalid_data(authenticated_client) -> None:
    """
    Test creating a movie with invalid data.
    """
    data = {
        "title": "",
        "year": 2010
    }

    response = authenticated_client.post(
        "/api/movies/",
        data,
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_update_movie(authenticated_client, movie) -> None:
    """
    Test updating a movie by its owner.
    """
    data = {
        "title": "Interstellar Updated",
        "description": "Updated description",
        "year": 2014,
        "duration_min": 169,
        "country": "USA",
        "rating": 9.0,
        "director": movie.director.id,
        "genres": []
    }

    response = authenticated_client.put(
        f"/api/movies/{movie.id}/",
        data,
        format="json"
    )

    assert response.status_code == 200
    assert response.data["title"] == "Interstellar Updated"


@pytest.mark.django_db
def test_update_movie_by_another_user(api_client, other_user, movie) -> None:
    """
    Test that another user cannot update someone else's movie.
    """
    api_client.force_authenticate(user=other_user)

    data = {
        "title": "Updated by another user",
        "description": "Test",
        "year": 2014,
        "director": movie.director.id,
        "genres": []
    }

    response = api_client.put(
        f"/api/movies/{movie.id}/",
        data,
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_movie(authenticated_client, movie) -> None:
    """
    Test deleting a movie by its owner.
    """
    response = authenticated_client.delete(
        f"/api/movies/{movie.id}/"
    )

    assert response.status_code == 204
    assert not Movie.objects.filter(id=movie.id).exists()


@pytest.mark.django_db
def test_delete_movie_by_another_user(api_client, other_user, movie) -> None:
    """
    Test that another user cannot delete someone else's movie.
    """
    api_client.force_authenticate(user=other_user)

    response = api_client.delete(
        f"/api/movies/{movie.id}/"
    )

    assert response.status_code == 403
    assert Movie.objects.filter(id=movie.id).exists()


@pytest.mark.django_db
def test_filter_movies_by_year(api_client, movie) -> None:
    """
    Test filtering movies by year.
    """
    response = api_client.get(
        "/api/movies/?year=2014",
        format="json"
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["year"] == 2014


@pytest.mark.django_db
def test_filter_movies_by_nonexistent_year(api_client, movie) -> None:
    """
    Test filtering movies by a year with no results.
    """
    response = api_client.get(
        "/api/movies/?year=2020",
        format="json"
    )

    assert response.status_code == 200
    assert response.data == []

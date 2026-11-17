import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from movies.models import Director, Movie


@pytest.fixture(scope="function")
def api_client() -> APIClient:
    """
    Fixture to provide an API client.

    :return: APIClient
    """
    yield APIClient()


@pytest.fixture(scope="function")
def user(db) -> User:
    """
    Fixture to provide a test user.

    :return: User
    """
    yield User.objects.create_user(
        username="testuser",
        password="testpassword123",
    )


@pytest.fixture(scope="function")
def other_user(db) -> User:
    """
    Fixture to provide another test user.

    :return: User
    """
    yield User.objects.create_user(
        username="otheruser",
        password="testpassword123",
    )


@pytest.fixture(scope="function")
def authenticated_client(api_client, user) -> APIClient:
    """
    Fixture to provide an authenticated API client.

    :return: APIClient
    """
    api_client.force_authenticate(user=user)
    yield api_client


@pytest.fixture(scope="function")
def director(db) -> Director:
    """
    Fixture to provide a test director.

    :return: Director
    """
    yield Director.objects.create(
        name="Christopher Nolan",
        country="USA",
    )


@pytest.fixture(scope="function")
def movie(db, user, director) -> Movie:
    """
    Fixture to provide a test movie.

    :return: Movie
    """
    yield Movie.objects.create(
        title="Interstellar",
        description="A science fiction film",
        year=2014,
        duration_min=169,
        country="USA",
        rating=8.7,
        director=director,
        owner=user,
    )

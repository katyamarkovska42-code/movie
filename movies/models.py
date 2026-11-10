from django.db import models


class Director(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    year = models.PositiveSmallIntegerField()
    duration_min = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    country = models.CharField(max_length=100, blank=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
    )
    director = models.ForeignKey(
        Director,
        on_delete=models.PROTECT,
        related_name="movies",
    )
    genres = models.ManyToManyField(
        Genre,
        related_name="movies",
        blank=True,
    )

    def __str__(self):
        return f"{self.title} ({self.year})"

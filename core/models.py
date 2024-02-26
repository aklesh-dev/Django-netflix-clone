from django.db import models
import uuid
from django.conf import settings

# Create your models here.
class Movie(models.Model):

    GENRA_CHOICES = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('horror', 'Horror'),
        ('romance', 'Romance'),
        ('science_fiction', 'Science Fiction'),
        ('thriller', 'Thriller')
    ]
    uu_id = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=100, choices=GENRA_CHOICES)
    length = models.PositiveIntegerField()  # in minutes
    image_card = models.ImageField(upload_to='movie_images/')
    image_cover = models.ImageField(upload_to='movie_images/')
    video = models.FileField(upload_to="movie_videos/")
    movie_views = models.IntegerField(default=0)

    def __str__(self) -> str:    
        return self.title
    
class MovieList(models.Model):
    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
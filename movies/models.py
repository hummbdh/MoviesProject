from django.db import models
from django.urls import reverse #Used to generate urls by reversing the URL patterns
import uuid # Required for unique film year

class FilmYear(models.Model):

    year = models.CharField(max_length=200)
    #film = models.ForeignKey('FilmYear', on_delete=models.SET_NULL, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def __str__(self):
        return self.year

    def get_absolute_url(self):
        return reverse('films', args=[str(self.id)])

from django.db import models
from un_app.models import Nation

class Resolution(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    votes_for = models.PositiveIntegerField()
    votes_against = models.PositiveIntegerField()
    proposed_by = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='proposed_resolution')
    body  = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    repealed = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.title} ({self.date})"
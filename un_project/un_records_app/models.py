from django.db import models

class Resolution(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    votes_for = models.PositiveIntegerField()
    votes_against = models.PositiveIntegerField()
    void = models.BooleanField(default=False)
    repealed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.date})"
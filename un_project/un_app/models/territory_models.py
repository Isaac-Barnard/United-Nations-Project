from django.db import models

class Territory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
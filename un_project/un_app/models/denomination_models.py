from django.db import models

class Denomination(models.Model):
    name = models.CharField(max_length=100, unique=True)
    diamond_equivalent = models.DecimalField(max_digits=20, decimal_places=15)
    priority = models.IntegerField(null=True)

    def __str__(self):
        return self.name
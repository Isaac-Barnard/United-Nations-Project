from django.db import models
#from .nation_models import Nation

class Player(models.Model):
    username = models.CharField(max_length=100, unique=True)
    nation = models.ForeignKey('Nation', on_delete=models.CASCADE, related_name='players')
    un_rep = models.BooleanField(default=False)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username
    
    def num_buildings_built(self):
        return self.main_builds.count()
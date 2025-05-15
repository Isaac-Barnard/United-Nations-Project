from django.db import models
from django.contrib.auth.models import User
#from .player_models import Player

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='user_profiles')

    def __str__(self):
        return f'{self.user.username} linked to {self.player.username}'
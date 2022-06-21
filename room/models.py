from django.db import models

# Create your models here.
from game.models import Player


class PlayerInQue(models.Model):
    # TODO use redis for storing
    player = models.ForeignKey(Player, unique=True, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.player.name} in que with score {self.score}"

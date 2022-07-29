from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.
from game.models import Player, Deck, Hero


class PlayerInQueue(models.Model):
    # TODO use redis for storing
    player = models.OneToOneField(Player, unique=True, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=50, blank=False)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.player.name} in que with score {self.score}"


class Room(models.Model):
    slug = models.SlugField(max_length=16, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    ended = models.BooleanField(default=False)

    def __str__(self):
        return f"room with slug {self.slug}"


class PlayerInRoom(models.Model):
    player = models.OneToOneField(Player, unique=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="players")
    first = models.BooleanField()
    score = models.IntegerField(blank=False)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="decks")
    online = models.BooleanField(default=False)
    channel_name = models.CharField(max_length=50, blank=True, null=True)

    def get_state(self):
        return GameState.objects.filter(player=self.player, room=self.room).last()

    def __str__(self):
        return f"{self.player.name} in room {self.room.slug}"


class GameState(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.IntegerField(blank=False)
    message = models.CharField(max_length=100, blank=False)

    class Meta:
        unique_together = ["room", "player", "round"]


class HeroInGame(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    player = models.ForeignKey(PlayerInRoom, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    # state on board
    x = models.IntegerField(
        blank=False, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    y = models.IntegerField(
        blank=False, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    health = models.IntegerField(blank=False)
    dead = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.hero.type} in room {self.room.slug}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.health and not self.dead:
            self.health = self.hero.health

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        unique_together = ["x", "y", "room"]

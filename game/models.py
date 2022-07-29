import random
import uuid

from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models

from chess_backend import settings
from common.generators import generate_charset
from game.services.jwt import sign_jwt


class HeroTypes(models.TextChoices):
    archer = "ARCHER", "archer"
    warrior = "WARRIOR", "warrior"
    wizard = "WIZARD", "wizard"
    king = "KING", "king"


class Player(models.Model):
    """base model to handle and store users"""

    ton_wallet = models.CharField(
        verbose_name="TON wallet",
        validators=[MinLengthValidator(48), MaxLengthValidator(48)],
        max_length=48,
        unique=True,
    )
    name = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def get_last_deck(self):
        return Deck.objects.filter(player=self).last()

    def get_auth_session(self):
        return PlayerAuthSession.objects.get(player=self).jit

    def get_refresh_token(self):
        return sign_jwt(
            {"jit": self.get_auth_session(), "type": "refresh"},
            t_life=settings.TOKEN_EXP,
        )

    def get_access_token(self):
        return sign_jwt({"id": self.id, "type": "access"}, t_life=settings.AUTH_EXP)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=["ton_wallet"])]
        ordering = ["-created"]

        db_table = "player"
        verbose_name = "player"
        verbose_name_plural = "players"


class Hero(models.Model):
    """Model to store heroes and their stats, connected to player"""

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="heroes",
        related_query_name="hero",
    )
    added = models.DateTimeField(auto_now_add=True)

    type = models.CharField(blank=False, choices=HeroTypes.choices, max_length=7)
    model_f = models.ForeignKey("HeroModelSet", on_delete=models.CASCADE)
    health = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], blank=False
    )
    attack = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], blank=False
    )
    speed = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], blank=False
    )

    def model(self):
        return self.model_f.model.url

    def __str__(self):
        return f"{self.type} {self.player.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.model_f = random.choice(HeroModelSet.objects.filter(hero_type=self.type))
        super(Hero, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        indexes = [models.Index(fields=["uuid"])]
        ordering = ["-added"]

        db_table = "hero"
        verbose_name = "hero"
        verbose_name_plural = "heroes"


class HeroModelSet(models.Model):
    hero_type = models.CharField(blank=False, choices=HeroTypes.choices, max_length=7)
    model = models.FileField(upload_to="uploads/")

    def __str__(self):
        return f"{self.hero_type} model file"


class Deck(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="decks",
        related_query_name="deck",
    )

    def __str__(self):
        return f"{self.player.name}'s deck"

    def get_heroes(self):
        return HeroInDeck.objects.filter(deck=self)

    def heroes(self):
        return self.get_heroes()

    def score(self):
        return sum(
            [x.hero.attack + x.hero.health + x.hero.speed for x in self.get_heroes()]
        )

    class Meta:
        db_table = "deck"
        verbose_name = "deck"
        verbose_name_plural = "decks"


class HeroInDeck(models.Model):
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name="hero_in_deck",
        related_query_name="heroes",
    )
    hero = models.OneToOneField(
        Hero,
        on_delete=models.CASCADE,
        related_name="hero_in_deck",
        related_query_name="decks",
    )
    x = models.IntegerField(
        blank=False, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    y = models.IntegerField(
        blank=False, validators=[MinValueValidator(1), MaxValueValidator(2)]
    )

    class Meta:
        db_table = "hero_in_deck"
        verbose_name = "Hero in deck"
        verbose_name_plural = "Heroes in decks"
        ordering = ["y", "x"]
        unique_together = ["deck", "x", "y"]


class PlayerAuthSession(models.Model):
    player = models.OneToOneField(
        Player, unique_for_month=True, on_delete=models.CASCADE
    )
    jit = models.CharField(max_length=30)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.jit = generate_charset(30)
        super(PlayerAuthSession, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

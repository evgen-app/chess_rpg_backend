import random
import uuid

from django.core.files import File
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.conf import settings

from common.generators import generate_charset

HER0_TYPES = [("WIZARD", "wizard"), ("ARCHER", "archer"), ("WARRIOR", "warrior")]


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

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """saves user and creates deck for him with 16 heroes"""
        super(Player, self).save()
        PlayerAuthSession.objects.create(player=self)
        deck = Deck.objects.create(player=self)
        types = (
            ["ARCHER" for _ in range(4)]
            + ["WARRIOR" for _ in range(6)]
            + ["WIZARD" for _ in range(2)]
            + [random.choice(HER0_TYPES)[0] for _ in range(4)]
        )
        for t in types:
            hero = Hero()
            hero.player = self
            hero.type = t

            # TODO: create image pool to generate heroes (awaiting for designer)
            with open(
                "/home/sanspie/Projects/chess_rpg_backend/media/dummy.jpg", "rb+"
            ) as file:
                hero.idle_img = File(file, name="dummy.jpg")
                hero.attack_img = File(file, name="dummy.jpg")
                hero.die_img = File(file, name="dummy.jpg")

                hero.health = random.randint(0, 10)
                hero.attack = random.randint(0, 10)
                hero.speed = random.randint(0, 10)

                hero.save()
                HeroInDeck.objects.create(deck=deck, hero=hero)

    def get_last_deck(self):
        return Deck.objects.filter(player=self).last()

    def get_auth_session(self):
        return PlayerAuthSession.objects.get(player=self).jit

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

    type = models.CharField(blank=False, choices=HER0_TYPES, max_length=7)
    idle_img = models.ImageField(upload_to="uploads/idle", blank=False)
    attack_img = models.ImageField(upload_to="uploads/attack", blank=False)
    die_img = models.ImageField(upload_to="uploads/die", blank=False)
    health = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], blank=False
    )
    attack = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], blank=False
    )
    speed = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], blank=False
    )

    def __str__(self):
        return f"{self.type} {self.player.name}"

    class Meta:
        indexes = [models.Index(fields=["uuid"])]
        ordering = ["-added"]

        db_table = "hero"
        verbose_name = "hero"
        verbose_name_plural = "heroes"


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
        return [x.hero for x in HeroInDeck.objects.filter(deck=self)]

    def heroes(self):
        # added for better DRF view
        return self.get_heroes()

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

    class Meta:
        db_table = "hero_in_deck"
        verbose_name = "Hero in deck"
        verbose_name_plural = "Heroes in decks"


class PlayerAuthSession(models.Model):
    player = models.OneToOneField(
        Player, unique_for_month=True, on_delete=models.CASCADE
    )
    jit = models.CharField(max_length=30, default=generate_charset(30))

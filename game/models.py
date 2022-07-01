import random
import uuid

from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models

from common.generators import generate_charset
from game.services.jwt import sign_jwt


class HeroTypes(models.TextChoices):
    wizard = "WIZARD", "wizard"
    archer = "ARCHER", "archer"
    warrior = "WARRIOR", "warrior"
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

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """saves user and creates deck for him with 16 heroes"""
        super(Player, self).save()
        PlayerAuthSession.objects.create(player=self)
        deck = Deck.objects.create(player=self)
        types = (
            ["KING"]
            + ["ARCHER" for _ in range(4)]
            + ["WARRIOR" for _ in range(6)]
            + ["WIZARD" for _ in range(2)]
            + [random.choice(HeroTypes.choices[:3])[0] for _ in range(3)]
        )
        for t in types:
            hero = Hero()
            hero.player = self
            hero.type = t

            hero.health = random.randint(0, 10)
            hero.attack = random.randint(0, 10)
            hero.speed = random.randint(0, 10)

            hero.save()
            HeroInDeck.objects.create(deck=deck, hero=hero)

    def get_last_deck(self):
        return Deck.objects.filter(player=self).last()

    def get_auth_session(self):
        return PlayerAuthSession.objects.get(player=self).jit

    def get_refresh_token(self):
        return sign_jwt({"jit": self.get_auth_session(), "type": "refresh"})

    def get_access_token(self):
        return sign_jwt({"id": self.id, "type": "access"}, t_life=3600)

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
    model = models.ForeignKey("HeroModelSet", on_delete=models.CASCADE)
    health = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], blank=False
    )
    attack = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], blank=False
    )
    speed = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], blank=False
    )

    def idle_img(self):
        return self.idle_img_f.image.url

    def attack_img(self):
        return self.attack_img_f.image.url

    def die_img(self):
        return self.die_img_f.image.url

    def __str__(self):
        return f"{self.type} {self.player.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.idle_img_f = random.choice(
            [x for x in HeroModelSet.objects.filter(hero_type=self.type)]
        )
        self.attack_img_f = random.choice(
            [x for x in HeroModelSet.objects.filter(hero_type=self.type)]
        )
        self.die_img_f = random.choice(
            [x for x in HeroModelSet.objects.filter(hero_type=self.type)]
        )
        super(Hero, self).save()

    class Meta:
        indexes = [models.Index(fields=["uuid"])]
        ordering = ["-added"]

        db_table = "hero"
        verbose_name = "hero"
        verbose_name_plural = "heroes"


class HeroModelSet(models.Model):
    hero_type = models.CharField(blank=False, choices=HeroTypes.choices, max_length=7)
    model = models.ImageField(upload_to="uploads/")

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
        return [x.hero for x in HeroInDeck.objects.filter(deck=self)]

    def heroes(self):
        # added for better DRF view
        return self.get_heroes()

    def score(self):
        return sum([x.attack + x.health + x.speed for x in self.get_heroes()])

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

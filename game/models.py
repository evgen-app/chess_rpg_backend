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
        super(Player, self).save()
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

            with open("/home/sanspie/Projects/chess_rpg_backend/media/dummy.jpg", "rb+") as file:
                hero.idle_img = File(file, name="dummy.jpg")
                hero.attack_img = File(file, name="dummy.jpg")
                hero.die_img = File(file, name="dummy.jpg")

                hero.health = random.randint(0, 10)
                hero.attack = random.randint(0, 10)
                hero.speed = random.randint(0, 10)

                hero.save()

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=["ton_wallet"])]
        ordering = ["-created"]
        verbose_name = "player"
        verbose_name_plural = "players"


class Hero(models.Model):
    """Model to store heroes and their stats, connected to player"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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
        verbose_name = "hero"
        verbose_name_plural = "heroes"

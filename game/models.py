import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

HER0_TYPES = [("WIZARD", "wizard"), ("ARCHER", "archer"), ("WARRIOR", "warrior")]


class Player(models.Model):
    """base model to handle and store users"""

    # TODO: connect real TON wallet
    ton_wallet = models.CharField(max_length=50, verbose_name="TON wallet")
    name = models.CharField(max_length=100, blank=True)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=["ton_wallet"])]
        ordering = ["-added"]
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

    type = models.CharField(blank=False, choices=HER0_TYPES, max_length=1)
    idle_img = models.ImageField(upload_to="uploads/idle", blank=False)
    attack_img = models.ImageField(upload_to="uploads/attack", blank=False)
    die_img = models.ImageField(upload_to="uploads/die", blank=False)
    health = models.IntegerField(
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

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, PlayerAuthSession
from .services.deck_handler import create_first_deck


@receiver(post_save, sender=Player)
def create_player(sender, instance, created, **kwargs):
    if created:
        PlayerAuthSession.objects.create(player=instance)
        create_first_deck(instance)

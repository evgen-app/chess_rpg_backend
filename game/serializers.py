from rest_framework import serializers

from game.models import Hero, Player


class CreateHeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = (
            "type",
            "idle_img",
            "attack_img",
            "die_img",
            "health",
            "attack",
            "speed",
        )


class GetHeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = (
            "added",
            "type",
            "idle_img",
            "attack_img",
            "die_img",
            "health",
            "attack",
            "speed",
        )


class CreatePlayerView(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("ton_wallet", "name")

from rest_framework import serializers

from game.models import Hero


class CreateHeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = ("type", "idle_img", "attack_img", "die_img", "health", "speed")


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
            "speed",
        )

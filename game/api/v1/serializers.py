from abc import ABC

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from game.models import Hero, Player, HeroInDeck, Deck


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


class ListHeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = (
            "uuid",
            "type",
            "idle_img",
            "attack_img",
            "die_img",
            "health",
            "attack",
            "speed",
        )


class CreatePlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("ton_wallet", "name")


class DeckCreateSerializer(serializers.ModelSerializer):
    hero_ids = serializers.ListSerializer(
        child=serializers.UUIDField(), min_length=16, max_length=16
    )

    class Meta:
        model = Deck
        fields = ("hero_ids",)

    def validate_hero_ids(self, value):
        for x in value:
            if not (hero := Hero.objects.filter(uuid=x)):
                raise ValidationError(f"Hero with uuid {x} doesn't exist")

            if deck := HeroInDeck.objects.filter(hero=hero.first()):
                raise ValidationError(
                    f"Hero with uuid {x} is already in deck with id {deck.first().deck.id}"
                )
        return value

    def create(self, validated_data):
        deck = Deck.objects.create(player=self.context["request"].user)
        for x in validated_data["hero_ids"]:
            HeroInDeck.objects.create(hero_id=x, deck=deck)
        return deck


class GetDeckSerializer(serializers.ModelSerializer):
    heroes = ListHeroSerializer(many=True)

    class Meta:
        model = Deck
        fields = ("player_uuid", "heroes")

    def get_heroes(self, val):
        print(val)

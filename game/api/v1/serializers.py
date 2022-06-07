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


class CreateDeckSerializer(serializers.ModelSerializer):
    hero_ids = serializers.ListSerializer(
        child=serializers.UUIDField(), min_length=16, max_length=16
    )

    class Meta:
        model = Deck
        fields = ("hero_ids",)

    def validate_hero_ids(self, value):
        if self.context["request"].method == "POST":
            for x in value:
                if not (hero := Hero.objects.filter(uuid=x)):
                    raise ValidationError(f"Hero with uuid {x} doesn't exist")

                if deck := HeroInDeck.objects.filter(hero=hero.first()):
                    raise ValidationError(
                        f"Hero with uuid {x} is already in deck with id {deck.first().deck.id}"
                    )
        elif self.context["request"].method in ["PUT", "PATCH"]:
            print(value)
        return value

    def create(self, validated_data):
        deck = Deck.objects.create(player=self.context["request"].user)
        for x in validated_data["hero_ids"]:
            HeroInDeck.objects.create(hero_id=x, deck=deck)
        return deck

    def update(self, instance, validated_data):
        print(instance, validated_data)
        return instance



class GetPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "name")


class GetDeckSerializer(serializers.ModelSerializer):
    player = GetPlayerSerializer()
    heroes = ListHeroSerializer(many=True)

    class Meta:
        model = Deck
        fields = ("player", "heroes")

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from game.models import Hero, Player, HeroInDeck, Deck, PlayerAuthSession
from game.services.jwt import read_jwt


class CreateHeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = (
            "type",
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
        if len(set(value)) != 16:
            raise ValidationError("Some of the uuids are not unique")

        for x in value:
            if not (hero := Hero.objects.filter(uuid=x)):
                raise ValidationError(f"Hero with uuid {x} doesn't exist")

            if hero.first().player.id != self.context["request"].user.id:
                raise ValidationError(
                    f"Attempt to manipulate player with id {hero.first().player.id} hero"
                )

            if self.context["request"].method in ["POST"]:
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

    def update(self, instance, validated_data):
        for x in instance.get_heroes():
            HeroInDeck.objects.get(hero=x).delete()

        for x in validated_data["hero_ids"]:
            HeroInDeck.objects.create(hero_id=x, deck=instance)

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


class ObtainTokenPairSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=300)

    def __init__(self, instance=None, data=None, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.player_id = None

    def validate_refresh_token(self, value):
        payload = read_jwt(value)
        if not payload:
            raise ValidationError("Token is incorrect or expired")

        if "jit" not in payload:
            raise ValidationError("Token is incorrect")

        jit = payload["jit"]

        try:
            session = PlayerAuthSession.objects.get(jit=jit)
        except PlayerAuthSession.DoesNotExist:
            return ValidationError("Incorrect user session")

        self.player_id = session.player.id
        return value

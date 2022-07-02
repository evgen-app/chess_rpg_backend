from rest_framework import status

from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response

from game.authentication import PlayerAuthentication
from game.models import Hero, Deck
from game.api.v1.serializers import (
    CreateHeroSerializer,
    GetHeroSerializer,
    CreatePlayerSerializer,
    ListHeroSerializer,
    CreateDeckSerializer,
    GetDeckSerializer,
    ObtainTokenPairSerializer,
)
from game.services.jwt import sign_jwt


class ListCreateHeroView(GenericAPIView, CreateModelMixin, ListModelMixin):
    authentication_classes = (PlayerAuthentication,)

    def perform_create(self, serializer):
        return serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        return Response({"uuid": instance.uuid}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListHeroSerializer
        else:
            return CreateHeroSerializer

    def get_queryset(self):
        return Hero.objects.filter(player_id=self.request.user.id)


class RetrieveHeroView(RetrieveModelMixin, UpdateAPIView, GenericAPIView):
    serializer_class = GetHeroSerializer
    lookup_field = "uuid"
    queryset = Hero.objects.all()

    def get_authenticators(self):
        if self.request.method != "GET":
            self.authentication_classes = [PlayerAuthentication]
        return [auth() for auth in self.authentication_classes]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class PlayerCreateView(GenericAPIView, CreateModelMixin):
    serializer_class = CreatePlayerSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        access_jwt = instance.get_access_token()
        refresh_jwt = instance.get_refresh_token()
        return Response(
            {
                "access_token": access_jwt,
                "refresh_token": refresh_jwt,
                "deck_id": instance.get_last_deck().id,
            },
            status=status.HTTP_201_CREATED,
        )


class DeckCreateView(GenericAPIView, CreateModelMixin):
    serializer_class = CreateDeckSerializer
    authentication_classes = (PlayerAuthentication,)

    def perform_create(self, serializer):
        return serializer.save(player=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        heroes_list = ListHeroSerializer(instance.get_heroes(), many=True)
        heroes_list.data["deck_id"] = instance.id
        return Response(heroes_list.data, status=status.HTTP_201_CREATED)


class RetireUpdateDeleteDeckView(
    RetrieveHeroView, DestroyModelMixin, UpdateModelMixin, GenericAPIView
):
    lookup_field = "id"
    queryset = Deck.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetDeckSerializer
        else:
            return CreateDeckSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        return serializer.update(self.get_object(), self.request.data)

    def put(self, request, *args, **kwargs):
        if not self._check_user_identity(kwargs["id"]):
            return Response(
                "Attempt to change another user's deck",
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        heroes_list = ListHeroSerializer(instance.get_heroes(), many=True)
        return Response(heroes_list.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        if not self._check_user_identity(kwargs["id"]):
            return Response(
                "Attempt to delete another user's deck",
                status=status.HTTP_403_FORBIDDEN,
            )
        self.destroy(request, *args, **kwargs)
        return Response(
            f"Destroyed deck with id {kwargs['id']}", status=status.HTTP_200_OK
        )

    def _check_user_identity(self, deck_id) -> bool:
        return deck_id in list(
            Deck.objects.filter(player_id=self.request.user.id).values_list(
                "id", flat=True
            )
        )


class RefreshAuthKey(GenericAPIView):
    serializer_class = ObtainTokenPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_jwt = sign_jwt(
            {"id": serializer.player_id, "type": "access"}, t_life=3600
        )
        return Response({"access_token": access_jwt}, status=status.HTTP_200_OK)

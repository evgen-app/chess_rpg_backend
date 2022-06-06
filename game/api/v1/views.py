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
from game.models import Hero
from game.api.v1.serializers import (
    CreateHeroSerializer,
    GetHeroSerializer,
    CreatePlayerSerializer,
    ListHeroSerializer,
    DeckCreateSerializer,
    GetDeckSerializer,
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
    authentication_classes = (PlayerAuthentication,)
    lookup_field = "uuid"
    queryset = Hero.objects.all()

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

        # TODO: add JTI to refresh token
        access_jwt = sign_jwt({"id": instance.id, "type": "access"}, t_life=3600)
        refresh_jwt = sign_jwt({"id": instance.id, "type": "refresh"})
        return Response(
            {"access_token": access_jwt, "refresh_token": refresh_jwt},
            status=status.HTTP_201_CREATED,
        )


class DeckCreateView(GenericAPIView, CreateModelMixin):
    serializer_class = DeckCreateSerializer
    authentication_classes = (PlayerAuthentication,)

    def perform_create(self, serializer):
        return serializer.save(player=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        heroes_list = ListHeroSerializer(instance.get_heroes(), many=True)
        return Response(heroes_list.data, status=status.HTTP_201_CREATED)


class RetireUpdateDeleteDeckView(
    RetrieveHeroView, DestroyModelMixin, UpdateModelMixin, GenericAPIView
):
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetDeckSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

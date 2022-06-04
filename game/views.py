from rest_framework import status

from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from game.models import Hero
from game.serializers import CreateHeroSerializer, GetHeroSerializer


class CreateHeroView(GenericAPIView, CreateModelMixin):
    serializer_class = CreateHeroSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        return Response({"uuid": instance.uuid}, status=status.HTTP_201_CREATED)


class RetrieveHeroView(RetrieveModelMixin, UpdateAPIView, GenericAPIView):
    serializer_class = GetHeroSerializer
    lookup_field = "uuid"
    queryset = Hero.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

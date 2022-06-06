from django.urls import path

from game.api.v1.views import (
    ListCreateHeroView,
    RetrieveHeroView,
    PlayerCreateView,
    DeckCreateView,
    RetireUpdateDeleteDeckView,
)

urlpatterns = [
    path("v1/hero/", ListCreateHeroView.as_view(), name="hero_api_create"),
    path("v1/hero/<uuid:uuid>", RetrieveHeroView.as_view(), name="hero_api_retrieve"),
    path("v1/player/", PlayerCreateView.as_view(), name="player_create_api"),
    path("v1/deck/", DeckCreateView.as_view(), name="deck_create_api"),
    path(
        "v1/deck/<int:pk>", RetireUpdateDeleteDeckView.as_view(), name="deck_retire_api"
    ),
]

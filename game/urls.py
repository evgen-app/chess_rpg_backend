from django.urls import path

from game.views import CreateHeroView, RetrieveHeroView, PlayerCreateView

urlpatterns = [
    path("hero/", CreateHeroView.as_view(), name="hero_api_create"),
    path("hero/<uuid:uuid>", RetrieveHeroView.as_view(), name="hero_api_retrieve"),
    path("player/", PlayerCreateView.as_view(), name="player_create_api"),
]

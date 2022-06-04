from django.urls import path

from game.views import CreateHeroView, RetrieveHeroView

urlpatterns = [
    path("hero/", CreateHeroView.as_view(), name="hero_api_create"),
    path("hero/<uuid:uuid>", RetrieveHeroView.as_view(), name="hero_api_retrieve"),
]
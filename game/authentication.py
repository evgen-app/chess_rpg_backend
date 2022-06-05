from rest_framework import authentication
from rest_framework import exceptions
from .models import Player
from .services.jwt import read_jwt


class PlayerAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers["Authorization"]
        if not token:
            raise exceptions.AuthenticationFailed("No credentials provided.")

        t = read_jwt(token)
        if not t:
            raise exceptions.AuthenticationFailed("Token is incorrect of expired")

        if "id" not in t:
            raise exceptions.AuthenticationFailed("No user data")

        try:
            user = Player.objects.get(id=int(t["id"]))
        except Player.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return user, None

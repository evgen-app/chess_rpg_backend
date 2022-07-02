from jwt import DecodeError
from rest_framework import authentication
from rest_framework import exceptions
from .models import Player
from .services.jwt import read_jwt


class PlayerAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        if "Authorization" not in request.headers or not (
            token := request.headers["Authorization"]
        ):
            raise exceptions.AuthenticationFailed("No credentials provided.")

        try:
            t = read_jwt(token)
        except DecodeError:
            raise exceptions.AuthenticationFailed("Token is incorrect")

        if not t:
            raise exceptions.AuthenticationFailed("Token is incorrect of expired")

        if "id" not in t and "type" not in t:
            raise exceptions.AuthenticationFailed("No user data")

        if t["type"] != "access":
            raise exceptions.AuthenticationFailed("Incorrect token type")

        try:
            user = Player.objects.get(id=int(t["id"]))
        except Player.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return user, None

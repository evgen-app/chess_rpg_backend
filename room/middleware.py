from channels.db import database_sync_to_async
from django.core.exceptions import PermissionDenied

from game.models import Player
from game.services.jwt import read_jwt


@database_sync_to_async
def get_player(jwt):
    payload = read_jwt(jwt)
    if not payload:
        raise PermissionDenied
    try:
        return Player.objects.get(id=payload)
    except User.DoesNotExist:
        return AnonymousUser()


class QueryAuthMiddleware:
    """Custom middleware to read user auth token from string."""

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        scope["user"] = await get_user(int(scope["query_string"]))

        return await self.app(scope, receive, send)

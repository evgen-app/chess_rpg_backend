import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

import room.routing
from room.middleware import HeaderAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chess_backend.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": HeaderAuthMiddleware(
            URLRouter(room.routing.websocket_urlpatterns)
        ),
    }
)

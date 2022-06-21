from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("room", consumers.QueConsumer.as_asgi()),
    path("room/<str:room_name>/", consumers.RoomConsumer.as_asgi()),
]

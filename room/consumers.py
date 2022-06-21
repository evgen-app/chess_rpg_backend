import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from game.models import Deck
from room.models import PlayerInQueue


class QueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "queue"

        await self.accept()
        await self.check_origin()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = None

        try:
            data = json.loads(text_data)
        except ValueError:
            await self.send(
                text_data=json.dumps(
                    {"type": "ERROR", "message": "data is not JSON serializable"}
                )
            )
        if data:
            # TODO move to external function/class
            if "type" not in data:
                await self.send(
                    text_data=json.dumps(
                        {"type": "ERROR", "message": "incorrect data typing"}
                    )
                )
            else:
                if data["type"] == "connect":
                    if "deck_id" not in data:
                        await self.send(
                            text_data=json.dumps(
                                {"type": "ERROR", "message": "deck id is not provided"}
                            )
                        )
                    else:
                        deck = None
                        # validate deck and check user originality
                        try:
                            deck_id = int(data["deck_id"])
                            deck = await self.check_user_deck(deck_id)
                        except ValueError:
                            await self.send(
                                text_data=json.dumps(
                                    {"type": "ERROR", "message": "deck id is incorrect"}
                                )
                            )
                        if deck:
                            await self.queue_connector(deck)
                        else:
                            await self.send(
                                text_data=json.dumps(
                                    {
                                        "type": "ERROR",
                                        "message": "such deck doesn't exist",
                                    }
                                )
                            )

    @sync_to_async
    def check_user_deck(self, deck_id: int):
        try:
            deck = Deck.objects.get(id=deck_id)
            if deck.player.id != self.scope["player"]:
                return False
            return deck
        except Deck.DoesNotExist:
            return False

    @sync_to_async
    def queue_connector(self, deck):
        try:
            queue = PlayerInQueue.objects.get(
                player_id=self.scope["player"]
            ).score = deck.score()
        except PlayerInQueue.DoesNotExist:
            queue = PlayerInQueue.objects.create(
                player_id=self.scope["player"], score=deck.score()
            )

        self.scope["queue"] = queue

    async def chat_message(self, event):
        pass

    async def check_origin(self):
        if not self.scope["player"]:
            await self.send(
                text_data=json.dumps(
                    {"type": "ERROR", "message": "token is incorrect or expired"}
                )
            )
            await self.close()


class RoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.room_name = None

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "room_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(text_data)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": text_data},
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"lot": message}))

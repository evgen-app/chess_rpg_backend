import json

from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from game.models import Deck
from room.models import PlayerInQueue


class QueueConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    async def connect(self):
        self.room_group_name = "queue"

        await self.accept()
        await self.check_origin()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.delete_user_in_queue()
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
                            # add to que, start finding players
                            await self.queue_connector(deck)
                            await self.send(
                                text_data=json.dumps(
                                    {
                                        "type": "INFO",
                                        "message": f"added to queue deck with score {self.scope['score']}",
                                    }
                                )
                            )
                            opponent = await self.find_user_by_score()

                            if not opponent:
                                await self.send(
                                    text_data=json.dumps(
                                        {
                                            "type": "INFO",
                                            "message": "no user found, awaiting in queue",
                                        }
                                    )
                                )
                            else:
                                # add to group and send message that opponent found to players
                                channel_layer = get_channel_layer()

                                await channel_layer.send(
                                    opponent[0],
                                    {
                                        "type": "info",
                                        "message": f"user found, with score {self.scope['score']}",
                                    },
                                )

                                await self.send(
                                    text_data=json.dumps(
                                        {
                                            "type": "INFO",
                                            "message": f"user found, with score {opponent[1]}",
                                        }
                                    )
                                )
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
    def delete_user_in_queue(self):
        try:
            PlayerInQueue.objects.get(player_id=self.scope["player"]).delete()
        except PlayerInQueue.DoesNotExist:
            return False

    @sync_to_async
    def find_user_by_score(self):
        s_min = self.scope["score"] * 0.95
        s_max = self.scope["score"] * 1.05
        for el in PlayerInQueue.objects.all():
            if el.player_id != self.scope["player"]:
                if s_min <= el.score <= s_max:
                    return el.channel_name, el.score
        return False

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
            queue = PlayerInQueue.objects.get(player_id=self.scope["player"])
            queue.score = deck.score()
            queue.channel_name = self.channel_name
            queue.save()

        except PlayerInQueue.DoesNotExist:
            queue = PlayerInQueue.objects.create(
                player_id=self.scope["player"],
                score=deck.score(),
                channel_name=self.channel_name,
            )

        self.scope["queue"] = queue.id
        self.scope["score"] = queue.score

    async def info(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"type": "INFO", "message": message}))

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
        self.room_group_name = f"room_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
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

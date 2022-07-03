import json
import os
import django

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chess_backend.settings")
django.setup()

from game.models import Deck
from room.models import PlayerInQueue, Room, PlayerInRoom, GameState
from room.services.room_create import create_room


class BaseConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

    async def send_message(self, message_type: str, **data):
        await self.send(text_data=json.dumps({"type": message_type, **data}))


class QueueConsumer(BaseConsumer):
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
            await self.send_message("ERROR", message="data is not JSON serializable")

        if data:
            # TODO move to external function/class
            if "type" not in data:
                await self.send_message("ERROR", message="incorrect data typing")
            else:
                if data["type"] == "connect":
                    if "deck_id" not in data:
                        await self.send_message(
                            "ERROR", message="deck id is not provided"
                        )
                    else:
                        deck = None
                        # validate deck and check user originality
                        try:
                            deck_id = int(data["deck_id"])
                            deck = await self.check_user_deck(deck_id)
                        except ValueError:
                            await self.send_message(
                                "ERROR", message="deck id is incorrect"
                            )

                        if deck:
                            # add to que, start finding players
                            await self.queue_connector(deck)
                            await self.send_message(
                                "INFO",
                                message=f"added to queue deck with score {self.scope['score']}",
                            )
                            opponent = await self.find_user_by_score()

                            if not opponent:
                                await self.send_message(
                                    "INFO", message="no user found, awaiting in queue"
                                )
                            else:
                                # add to group and send message that opponent found to players
                                room = await create_room(
                                    deck_id_1=self.scope["deck"],
                                    player_id_1=self.scope["player"],
                                    player_score_1=self.scope["score"],
                                    deck_id_2=opponent[2],
                                    player_id_2=opponent[3],
                                    player_score_2=opponent[1],
                                )

                                await self.channel_layer.send(
                                    opponent[0],
                                    {
                                        "type": "info",
                                        "message": f"user found, with score {self.scope['score']}",
                                        "room": room,
                                    },
                                )

                                await self.send_message(
                                    "INFO",
                                    message=f"user found, with score {opponent[1]}",
                                    room=room,
                                )
                        else:
                            await self.send_message(
                                "ERROR", message="such deck doesn't exist"
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
                    return el.channel_name, el.score, el.deck.id, el.player.id
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
                deck=deck,
                score=deck.score(),
                channel_name=self.channel_name,
            )

        self.scope["queue"] = queue.id
        self.scope["deck"] = deck.id
        self.scope["score"] = queue.score

    async def info(self, event):
        if "room" in event:
            await self.send_message(
                "INFO", message=event["message"], room=event["room"]
            )
        else:
            await self.send_message("INFO", message=event["message"])

    async def check_origin(self):
        if not self.scope["player"]:
            await self.send_message("ERROR", message="token is incorrect or expired")
            await self.close()


class RoomConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.room_name = None

    async def connect(self):
        await self.accept()
        await self.check_origin()

        if not await self.connect_to_room():
            await self.close()
        else:
            message, round = await self.get_state()

            await self.send_message(
                "INFO",
                opponent_score=self.scope["opponent_score"],
                opponent_deck=self.scope["opponent_deck"],
                opponent_online=self.scope["opponent_online"],
                first=self.scope["first"],
                state=message,
                round=round,
            )
            if "opponent_channel" in self.scope and self.scope["opponent_channel"]:
                await self.channel_layer.send(
                    self.scope["opponent_channel"],
                    {
                        "type": "channel",
                        "channel": self.channel_name,
                    },
                )
                await self.channel_layer.send(
                    self.scope["opponent_channel"],
                    {"type": "connection_info", "online": True},
                )

            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    @sync_to_async
    def get_state(self):
        state = self.scope["player_in_room"].get_state()
        return state.message, state.round

    @sync_to_async
    def connect_to_room(self):
        slug = self.scope["url_route"]["kwargs"]["room_name"]

        self.room_name = slug
        self.room_group_name = f"room_{slug}"
        room = Room.objects.filter(slug=slug)

        if not room:
            return False

        self.scope["room"] = room

        # check if player can be in a room
        p_ids = [x.player.id for x in room.first().players.all()]
        if self.scope["player"] not in p_ids:
            return False

        # add player info to scope
        player = PlayerInRoom.objects.get(player_id=self.scope["player"])

        self.scope["player_in_room"] = player
        self.scope["first"] = player.first
        self.scope["score"] = player.score
        self.scope["deck"] = player.deck.id

        p_ids.remove(player.player.id)
        opponent = PlayerInRoom.objects.get(player_id=p_ids[0])

        self.scope["opponent"] = opponent.player.id
        self.scope["opponent_channel"] = opponent.channel_name
        self.scope["opponent_score"] = opponent.score
        self.scope["opponent_deck"] = opponent.deck.id
        self.scope["opponent_first"] = opponent.first
        self.scope["opponent_online"] = opponent.online

        player.online = True
        player.channel_name = self.channel_name
        player.save(update_fields=["online", "channel_name"])
        return True

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.disconnect_player()

        if "opponent_channel" in self.scope and self.scope["opponent_channel"]:
            await self.channel_layer.send(
                self.scope["opponent_channel"],
                {"type": "connection_info", "online": False},
            )

    @sync_to_async
    def disconnect_player(self):
        if "player_in_room" in self.scope:
            self.scope["player_in_room"].online = False
            self.scope["player_in_room"].channel_name = None
            self.scope["player_in_room"].save(update_fields=["online", "channel_name"])

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = None

        try:
            data = json.loads(text_data)
        except ValueError:
            await self.send_message("ERROR", message="data is not JSON serializable")

        if data:
            if data["type"] == "start":
                if not await self.start(data):
                    await self.send_message("ERROR", message="opponent is offline")

    async def start(self, data):
        if self.scope["opponent_channel"] and self.scope["opponent_online"]:
            await self.channel_layer.send(
                self.scope["opponent_channel"],
                {
                    "type": "info",
                    "message": "opponent is ready to start",
                },
            )
            return True
        return False

    # info type group message handler
    async def info(self, event):
        message = event["message"]
        msg = {"type": "INFO", "message": message}

        if "opponent_score" in event:
            msg["opponent_score"] = event["opponent_score"]

        if "opponent_deck" in event:
            msg["opponent_deck"] = event["opponent_deck"]

        if "opponent_online" in event:
            msg["opponent_online"] = event["opponent_online"]

        if "first" in event:
            msg["first"] = event["first"]

        if "state" in event:
            msg["state"] = event["state"]

        if "round" in event:
            msg["round"] = event["round"]

        await self.send(text_data=json.dumps(msg))

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"lot": message}))

    async def channel(self, event):
        channel = event["channel"]
        self.scope["opponent_channel"] = channel

    async def connection_info(self, event):
        status = event["online"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "INFO",
                    "message": "opponent is online"
                    if status
                    else "opponent is offline",
                }
            )
        )
        self.scope["opponent_online"] = status

    async def check_origin(self):
        if not self.scope["player"]:
            await self.send(
                text_data=json.dumps(
                    {"type": "ERROR", "message": "token is incorrect or expired"}
                )
            )
            await self.close()

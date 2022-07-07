from asgiref.sync import sync_to_async
from random import randint

from common.generators import generate_charset
from game.models import Player, Deck
from room.models import Room, PlayerInRoom, GameState, HeroInGame


@sync_to_async
def create_room(
    deck_id_1: int,
    player_id_1: int,
    player_score_1: int,
    deck_id_2: int,
    player_id_2: int,
    player_score_2: int,
) -> str:
    room = Room.objects.create(slug=generate_charset(16))
    player_1 = Player.objects.get(id=player_id_1)
    player_2 = Player.objects.get(id=player_id_2)

    first_player = randint(1, 2)

    p1 = PlayerInRoom.objects.create(
        player=player_1,
        room=room,
        score=player_score_1,
        deck_id=deck_id_1,
        first=first_player == 1,
    )

    p2 = PlayerInRoom.objects.create(
        player=player_2,
        room=room,
        score=player_score_2,
        deck_id=deck_id_2,
        first=first_player == 2,
    )
    for p, d_id in [(p1, deck_id_1), (p2, deck_id_2)]:
        GameState.objects.create(room=room, player=p, round=0, message="Game started")
        for hero in Deck.objects.get(id=d_id).heroes.all():
            if p.first:
                HeroInGame.objects.create(
                    hero=hero, player=p, room=room, x=hero.x, y=hero.y
                )
            else:
                HeroInGame.objects.create(
                    hero=hero, player=p, room=room, x=hero.x, y=8 - hero.y
                )
    return room.slug

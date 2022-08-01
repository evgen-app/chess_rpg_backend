from common.generators import gen_ton
from game.models import Player, Deck, Hero
from room.services.room_create import sync_create_room


def _check_players_score(players):
    for player in players:
        for player2 in players:
            if player != player2:
                s_min = players[player] * 0.95
                s_max = players[player] * 1.05
                if s_min <= players[player2] <= s_max:
                    return False
    return True


def generate_room():
    players = {}

    for _ in range(2):
        player = Player.objects.create(ton_wallet=gen_ton())
        players[player] = player.get_last_deck().score()

    while _check_players_score(players):
        player = Player.objects.create(ton_wallet=gen_ton())
        players[player] = player.get_last_deck().score()

    for player in players:
        for player2 in players:
            if player != player2:
                s_min = players[player] * 0.95
                s_max = players[player] * 1.05
                if s_min <= players[player2] <= s_max:
                    p1 = player
                    p2 = player2

    room_slug = sync_create_room(
        p1.get_last_deck().id,
        p1.id,
        players[p1],
        p2.get_last_deck().id,
        p2.id,
        players[p2],
    )
    print(f"ws://127.0.0.1:8000/room/{room_slug}")
    print(f"Authorization: {p1.get_access_token()}")
    print(f"Authorization: {p2.get_access_token()}")
    return None

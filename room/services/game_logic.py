from asgiref.sync import sync_to_async
from termcolor import colored

from room.models import HeroInGame, Room, PlayerInRoom


def _check_path(f_x: int, f_y: int, x: int, y: int, room: Room, move_type: str):
    if move_type == "DIAGONAL":
        return (
            HeroInGame.objects.filter(
                room=room, x__range=(f_x, x), y__range=(f_y, y)
            ).count()
            == 0
        )
    elif move_type == "HORIZONTAL":
        return HeroInGame.objects.filter(room=room, x=x, y__range=(f_y, y)).count() == 0
    elif move_type == "VERTICAL":
        return HeroInGame.objects.filter(room=room, x__range=(f_x, x), y=y).count() == 0
    return False


def _validate_hero_movement(
    hero_type: str,
    prev_x: int,
    prev_y: int,
    x: int,
    y: int,
    room: Room,
    first: bool = False,  # needed for warrior
):
    if hero_type == "KING":
        if abs(x - prev_x) > 1 or abs(y - prev_y) > 1:
            return False
    elif hero_type == "WIZARD":
        if abs(x - prev_x) == abs(y - prev_y):
            return _check_path(prev_x, prev_y, x, y, room, "DIAGONAL")
        elif x == prev_x and y != prev_y:
            return _check_path(prev_x, prev_y, x, y, room, "HORIZONTAL")
        elif x != prev_x and y == prev_y:
            return _check_path(prev_x, prev_y, x, y, room, "VERTICAL")
        return False
    elif hero_type == "ARCHER":
        if abs(x - prev_x) == abs(y - prev_y):
            return _check_path(prev_x, prev_y, x, y, room, "DIAGONAL")
        return False
    elif hero_type == "WARRIOR":
        if first:
            if x == prev_x and y - prev_y == 1:
                return True
            elif abs(x - prev_x) == 1 and y - prev_y == 1:
                return True
        else:
            if x == prev_x and prev_y - y == 1:
                return True
    return False


def _print_board(room: Room):
    for y in range(1, 8):
        for x in range(1, 9):
            try:
                hero = HeroInGame.objects.get(x=x, y=y, room=room)
                if hero.hero.type == "KING":
                    if hero.player.first:
                        print(colored("♔", 'green', attrs=['bold']), end="")
                    else:
                        print(colored("♚", 'red', attrs=['bold']), end="")
                elif hero.hero.type == "WIZARD":
                    if hero.player.first:
                        print(colored("♕", 'green', attrs=['bold']), end="")
                    else:
                        print(colored("♛", 'red', attrs=['bold']), end="")
                elif hero.hero.type == "ARCHER":
                    if hero.player.first:
                        print(colored("♗", 'green', attrs=['bold']), end="")
                    else:
                        print(colored("♝", 'red', attrs=['bold']), end="")
                else:
                    if hero.player.first:
                        print(colored("♙", 'green', attrs=['bold']), end="")
                    else:
                        print(colored("♟", 'red', attrs=['bold']), end="")
            except HeroInGame.DoesNotExist:
                print("*", end="")
        print()


@sync_to_async
def move_handler(
    prev_x: int, prev_y: int, x: int, y: int, room_slug: str, player: PlayerInRoom
):
    room = Room.objects.get(slug=room_slug)
    _print_board(room)  # TODO: Remove in production
    try:
        hero = HeroInGame.objects.get(x=prev_x, y=prev_y, room=room, player=player)
    except HeroInGame.DoesNotExist:
        return False

    if x == prev_x and y == prev_y:
        return False

    h_t = hero.hero.type

    _print_board(room)  # TODO: Remove in production

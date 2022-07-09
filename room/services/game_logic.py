from room.models import HeroInGame, Room, PlayerInRoom


def _check_move_position(x: int, y: int, room: Room, p_first: bool):
    hero = HeroInGame.objects.filter(x=x, y=y, room=room)
    if not hero.exists():
        return False
    elif hero.first()


def move_handler(prev_x: int, prev_y: int, x: int, y: int, room: Room, player: PlayerInRoom):
    try:
        hero = HeroInGame.objects.get(x=prev_x, y=prev_y, room=room, player=player)
    except HeroInGame.DoesNotExist:
        return False

    h_t = hero.hero.type
    if h_t == "KING":
        if abs(prev_x - x) != 1 or abs(prev_y - y) != 1:
            return False
    elif h_t == "WARRIOR":
        if player.first:
            if x - prev_x == 1 and y - prev_y == 0:
                _check_move_position(x, y, room, True)

